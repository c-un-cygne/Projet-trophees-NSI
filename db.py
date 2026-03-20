import os
import libsql
from dotenv import load_dotenv

rep_base = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(rep_base, ".gitignore/data.env"))

db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")

def get_conn():
    return libsql.connect(database=db_url, auth_token=db_token)

def rechercher_activites(query: str, categorie: str = "") -> list[dict]:
    """Retourne les activités filtrées par texte libre et/ou catégorie."""
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
    return [
        {"id": r[0], "category": r[1], "name": r[2], "factor": r[3], "unit": r[4]}
        for r in rows
    ]


def get_categories() -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT category FROM activities ORDER BY category").fetchall()
    conn.close()
    return [r[0] for r in rows]


def ajouter_entree_carbone(user_id: int, activity_id: int, quantity: float) -> float:
    """Insère une entrée dans carbon_history. Retourne le CO2 en kg."""
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
    return co2_kg


def get_total_co2(user_id: int) -> float:
    """Retourne le total CO2 (kg) de l'utilisateur."""
    conn = get_conn()
    row = conn.execute(
        "SELECT COALESCE(SUM(co2_kg), 0) FROM carbon_history WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row[0]


def recuperer_demandes_amis(user_id):
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