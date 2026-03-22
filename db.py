import os
import libsql
import time
from dotenv import load_dotenv

rep_base = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(rep_base, ".gitignore/data.env"))

db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")

# on garde en mémoire certaines données pour pas refaire des requêtes inutiles
cache = {
    "categories": None,
    "categories_ts": 0,
    "co2": {},        # {user_id: (valeur, timestamp)}
    "recherche": {},  # {(query, cat): (resultats, timestamp)}
}

TTL_CATEGORIES = 300
TTL_CO2 = 60
TTL_RECHERCHE = 120


def get_conn():
    return libsql.connect(database=db_url, auth_token=db_token)


def rechercher_activites(query, categorie=""):
    cle = (query, categorie)

    if cle in cache["recherche"]:
        res, ts = cache["recherche"][cle]
        if time.time() - ts < TTL_RECHERCHE:
            return res

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

    res = [{"id": i[0], "category": i[1], "name": i[2], "factor": i[3], "unit": i[4]} for i in rows]
    cache["recherche"][cle] = (res, time.time())
    return res


def get_categories():
    if cache["categories"] and time.time() - cache["categories_ts"] < TTL_CATEGORIES:
        return cache["categories"]

    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT category FROM activities ORDER BY category").fetchall()
    conn.close()

    cache["categories"] = [i[0] for i in rows]
    cache["categories_ts"] = time.time()
    return cache["categories"]


def ajouter_entree_carbone(user_id, activity_id, quantite):
    conn = get_conn()
    row = conn.execute("SELECT factor FROM activities WHERE id=?", (activity_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Activité {activity_id} introuvable")

    co2_kg = row[0] * quantite
    conn.execute("INSERT INTO carbon_history (user_id, activity_id, quantity, co2_kg) VALUES (?, ?, ?, ?)", (user_id, activity_id, quantite, co2_kg))
    conn.commit()
    conn.close()

    # on vide le cache co2 de cet user pour forcer le recalcul
    cache["co2"].pop(user_id, None)
    return co2_kg


def get_total_co2(user_id):
    if user_id in cache["co2"]:
        val, ts = cache["co2"][user_id]
        if time.time() - ts < TTL_CO2:
            return val

    conn = get_conn()
    row = conn.execute("SELECT SUM(co2_kg) FROM carbon_history WHERE user_id=?", (user_id,)).fetchone()
    conn.close()

    val = row[0] if row[0] else 0
    cache["co2"][user_id] = (val, time.time())
    return val


def get_friends_count(user_id):
    conn = get_conn()
    # on fait deux requêtes et on additionne, plus simple à comprendre
    amis1 = conn.execute("SELECT COUNT(*) FROM friendships WHERE user_id=? AND status='friends'", (user_id,)).fetchone()[0]
    amis2 = conn.execute("SELECT COUNT(*) FROM friendships WHERE friend_id=? AND status='friends'", (user_id,)).fetchone()[0]
    conn.close()
    return amis1 + amis2


def recuperer_demandes_amis(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT users.username FROM friendships JOIN users ON friendships.user_id = users.id WHERE friendships.friend_id = ? AND friendships.status = 'pending'",
        (user_id,),
    ).fetchall()
    conn.close()
    return [i[0] for i in rows]


def get_friends_list(user_id):
    conn = get_conn()
    amis1 = conn.execute("SELECT users.username FROM friendships JOIN users ON friendships.friend_id = users.id WHERE friendships.user_id=? AND friendships.status='friends'", (user_id,)).fetchall()
    amis2 = conn.execute("SELECT users.username FROM friendships JOIN users ON friendships.user_id = users.id WHERE friendships.friend_id=? AND friendships.status='friends'", (user_id,)).fetchall()
    conn.close()
    return list(set([i[0] for i in amis1 + amis2]))


def accept_friend_request(user_id, demandeur):
    conn = get_conn()
    res = conn.execute("SELECT id FROM users WHERE username=?", (demandeur,)).fetchone()
    if not res:
        conn.close()
        return False

    demandeur_id = res[0]
    demande = conn.execute("SELECT id FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'", (demandeur_id, user_id)).fetchone()
    if not demande:
        conn.close()
        return False

    conn.execute("DELETE FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'", (demandeur_id, user_id))
    conn.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'friends')", (demandeur_id, user_id))
    conn.commit()
    conn.close()
    return True


def refuse_friend_request(user_id, demandeur):
    conn = get_conn()
    res = conn.execute("SELECT id FROM users WHERE username=?", (demandeur,)).fetchone()
    if not res:
        conn.close()
        return False

    conn.execute("DELETE FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'", (res[0], user_id))
    conn.commit()
    conn.close()
    return True


def send_friend_request(user_id, cible):
    conn = get_conn()
    res = conn.execute("SELECT id FROM users WHERE username=?", (cible,)).fetchone()
    if not res:
        conn.close()
        return "not_found"

    cible_id = res[0]
    if cible_id == user_id:
        conn.close()
        return "self"

    deja = conn.execute("SELECT id FROM friendships WHERE user_id=? AND friend_id=?", (user_id, cible_id)).fetchone()
    if deja:
        conn.close()
        return "already_sent"

    conn.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'pending')", (user_id, cible_id))
    conn.commit()
    conn.close()
    return "success"


def remove_friend(user_id, ami):
    conn = get_conn()
    res = conn.execute("SELECT id FROM users WHERE username=?", (ami,)).fetchone()
    if not res:
        conn.close()
        return False

    ami_id = res[0]
    conn.execute("DELETE FROM friendships WHERE ((user_id=? AND friend_id=?) OR (user_id=? AND friend_id=?)) AND status='friends'", (user_id, ami_id, ami_id, user_id))
    conn.commit()
    conn.close()
    return True