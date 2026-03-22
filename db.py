import os
import libsql
import time
from dotenv import load_dotenv
from functools import lru_cache

rep_base = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(rep_base, ".gitignore/data.env"))

db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")

# Cache global pour les données qui changent peu souvent
_cache = {
    "categories": None,
    "categories_timestamp": 0,
    "co2_cache": {},  # {user_id: (value, timestamp)}
    "search_cache": {},  # {(query, categorie): (results, timestamp)}
}

CACHE_TTL = 300  # 5 minutes en secondes
CO2_CACHE_TTL = 60  # 1 minute pour le CO2 (changements fréquents)
SEARCH_CACHE_TTL = 120  # 2 minutes pour la recherche

def get_conn():
    """Retourne une connexion à la base de données."""
    return libsql.connect(database=db_url, auth_token=db_token)

def invalidate_co2_cache(user_id: int):
    """Invalide le cache du CO2 pour un utilisateur."""
    if user_id in _cache["co2_cache"]:
        del _cache["co2_cache"][user_id]

def invalidate_search_cache():
    """Invalide tout le cache de recherche."""
    _cache["search_cache"].clear()

def _is_cache_valid(timestamp: int, ttl: int) -> bool:
    """Vérifie si un cache est encore valide."""
    return (time.time() - timestamp) < ttl

def rechercher_activites(query: str, categorie: str = "") -> list[dict]:
    """
    Retourne les activités filtrées par texte libre et/ou catégorie.
    Utilise un cache avec TTL pour éviter les requêtes répétées.
    """
    cache_key = (query, categorie)
    
    # Vérifier le cache
    if cache_key in _cache["search_cache"]:
        results, timestamp = _cache["search_cache"][cache_key]
        if _is_cache_valid(timestamp, SEARCH_CACHE_TTL):
            return results
    
    # Pas en cache ou expiré → requête DB
    conn = get_conn()
    sql = "SELECT id, category, name, factor, unit FROM activities WHERE 1=1"
    params = []
    if categorie:
        sql += " AND category = ?"
        params.append(categorie)
    if query:
        sql += " AND name LIKE ?"
        params.append(f"%{query}%")
    sql += " ORDER BY category, name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    
    results = [
        {"id": r[0], "category": r[1], "name": r[2], "factor": r[3], "unit": r[4]}
        for r in rows
    ]
    
    # Stocker en cache
    _cache["search_cache"][cache_key] = (results, time.time())
    
    return results


def get_categories() -> list[str]:
    """
    Retourne les catégories d'activités.
    Les catégories sont mises en cache car elles ne changent jamais.
    """
    # Vérifier le cache
    if _cache["categories"] is not None:
        if _is_cache_valid(_cache["categories_timestamp"], CACHE_TTL):
            return _cache["categories"]
    
    # Pas en cache ou expiré → requête DB
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT category FROM activities ORDER BY category"
    ).fetchall()
    conn.close()
    
    categories = [r[0] for r in rows]
    
    # Stocker en cache
    _cache["categories"] = categories
    _cache["categories_timestamp"] = time.time()
    
    return categories


def ajouter_entree_carbone(user_id: int, activity_id: int, quantity: float) -> float:
    """
    Insère une entrée dans carbon_history. Retourne le CO2 en kg.
    Invalide le cache du CO2 après insertion.
    """
    conn = get_conn()
    row = conn.execute("SELECT factor FROM activities WHERE id=?", (activity_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Activité {activity_id} introuvable")
    co2_kg = row[0] * quantity
    conn.execute(
        "INSERT INTO carbon_history (user_id, activity_id, quantity, co2_kg) VALUES (?, ?, ?, ?)",
        (user_id, activity_id, quantity, co2_kg),
    )
    conn.commit()
    conn.close()
    
    # Invalider le cache du CO2 pour cet utilisateur
    invalidate_co2_cache(user_id)
    
    return co2_kg


def get_total_co2(user_id: int) -> float:
    """
    Retourne le total CO2 (kg) de l'utilisateur.
    Utilise un cache avec invalidation après chaque nouvelle entrée.
    """
    # Vérifier le cache
    if user_id in _cache["co2_cache"]:
        value, timestamp = _cache["co2_cache"][user_id]
        if _is_cache_valid(timestamp, CO2_CACHE_TTL):
            return value
    
    # Pas en cache ou expiré → requête DB
    conn = get_conn()
    row = conn.execute(
        "SELECT COALESCE(SUM(co2_kg), 0) FROM carbon_history WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    
    value = row[0]
    
    # Stocker en cache
    _cache["co2_cache"][user_id] = (value, time.time())
    
    return value


def get_friends_count(user_id: int) -> int:
    """
    Retourne le nombre total d'amis (bidirectionnels).
    Optimisée en une seule requête.
    """
    conn = get_conn()
    # Compte les amis des deux côtés en une seule requête
    row = conn.execute("""
        SELECT COUNT(DISTINCT 
            CASE 
                WHEN user_id = ? AND status = 'friends' THEN friend_id
                WHEN friend_id = ? AND status = 'friends' THEN user_id
            END
        ) FROM friendships
        WHERE (user_id = ? OR friend_id = ?) AND status = 'friends'
    """, (user_id, user_id, user_id, user_id)).fetchone()
    conn.close()
    return row[0] if row else 0


def recuperer_demandes_amis(user_id):
    """Retourne les demandes d'amis en attente."""
    conn = get_conn()
    demandes = conn.execute(
        """
        SELECT users.username FROM friendships
        JOIN users ON friendships.user_id = users.id
        WHERE friendships.friend_id = ? AND friendships.status = 'pending'
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return [i[0] for i in demandes]


def get_friends_list(user_id: int) -> list[str]:
    """
    Récupère la liste de tous les amis (bidirectionnels) en une seule requête.
    Bien plus efficace que deux requêtes séparées.
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT DISTINCT u.username 
        FROM friendships f
        JOIN users u ON (
            (f.user_id = ? AND f.friend_id = u.id) OR
            (f.friend_id = ? AND f.user_id = u.id)
        )
        WHERE f.status = 'friends'
        ORDER BY u.username
    """, (user_id, user_id)).fetchall()
    conn.close()
    return [r[0] for r in rows]


def accept_friend_request(user_id: int, requesting_username: str) -> bool:
    """
    Accepte une demande d'ami. Retourne True si succès, False sinon.
    """
    conn = get_conn()
    try:
        # Récupérer l'ID de l'utilisateur qui a envoyé la demande
        requesting_user = conn.execute(
            "SELECT id FROM users WHERE username=?", (requesting_username,)
        ).fetchone()
        
        if not requesting_user:
            return False
        
        requesting_id = requesting_user[0]
        
        # Vérifier qu'il y a une demande pending
        existing = conn.execute("""
            SELECT id FROM friendships
            WHERE user_id = ? AND friend_id = ? AND status = 'pending'
        """, (requesting_id, user_id)).fetchone()
        
        if not existing:
            conn.close()
            return False
        
        # Supprimer la demande et ajouter l'amitié
        conn.execute(
            "DELETE FROM friendships WHERE user_id = ? AND friend_id = ? AND status = 'pending'",
            (requesting_id, user_id)
        )
        conn.execute("""
            INSERT INTO friendships (user_id, friend_id, status) 
            VALUES (?, ?, 'friends')
        """, (requesting_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Erreur accept_friend_request: {e}")
        return False


def refuse_friend_request(user_id: int, requesting_username: str) -> bool:
    """
    Refuse une demande d'ami. Retourne True si succès, False sinon.
    """
    conn = get_conn()
    try:
        # Récupérer l'ID de l'utilisateur qui a envoyé la demande
        requesting_user = conn.execute(
            "SELECT id FROM users WHERE username=?", (requesting_username,)
        ).fetchone()
        
        if not requesting_user:
            return False
        
        requesting_id = requesting_user[0]
        
        # Supprimer la demande
        conn.execute("""
            DELETE FROM friendships
            WHERE user_id = ? AND friend_id = ? AND status = 'pending'
        """, (requesting_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Erreur refuse_friend_request: {e}")
        return False


def send_friend_request(user_id: int, target_username: str) -> str:
    """
    Envoie une demande d'ami. 
    Retourne 'success', 'not_found', 'self', ou 'already_sent'
    """
    conn = get_conn()
    try:
        # Vérifier que l'utilisateur cible existe
        target = conn.execute(
            "SELECT id FROM users WHERE username=?", (target_username,)
        ).fetchone()
        
        if not target:
            conn.close()
            return "not_found"
        
        target_id = target[0]
        
        # Vérifier qu'on ne s'envoie pas une demande à soi-même
        if target_id == user_id:
            conn.close()
            return "self"
        
        # Vérifier qu'une demande n'a pas déjà été envoyée
        existing = conn.execute("""
            SELECT id FROM friendships 
            WHERE user_id = ? AND friend_id = ?
        """, (user_id, target_id)).fetchone()
        
        if existing:
            conn.close()
            return "already_sent"
        
        # Envoyer la demande
        conn.execute("""
            INSERT INTO friendships (user_id, friend_id, status) 
            VALUES (?, ?, 'pending')
        """, (user_id, target_id))
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        conn.close()
        print(f"Erreur send_friend_request: {e}")
        return "error"


def remove_friend(user_id: int, friend_username: str) -> bool:
    """
    Supprime un ami. Retourne True si succès, False sinon.
    """
    conn = get_conn()
    try:
        # Récupérer l'ID de l'ami
        friend = conn.execute(
            "SELECT id FROM users WHERE username=?", (friend_username,)
        ).fetchone()
        
        if not friend:
            conn.close()
            return False
        
        friend_id = friend[0]
        
        # Supprimer les deux côtés de l'amitié
        conn.execute("""
            DELETE FROM friendships
            WHERE ((user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?))
            AND status = 'friends'
        """, (user_id, friend_id, friend_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Erreur remove_friend: {e}")
        return False