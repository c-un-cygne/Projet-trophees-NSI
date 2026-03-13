import os
import libsql
from dotenv import load_dotenv

rep_base = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(rep_base, ".gitignore/data.env"))

db_url = os.getenv("TURSO_DATABASE_URL")
db_token = os.getenv("TURSO_AUTH_TOKEN")


def get_conn():
    return libsql.connect(database=db_url, auth_token=db_token)


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
