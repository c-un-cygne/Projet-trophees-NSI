from kivymd.uix.dialog import MDDialog

from db import get_conn, recuperer_demandes_amis
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis


class FriendsMixin:
    """
    Mixin à hériter par TerraGaugeApp.
    Regroupe toute la logique liée aux amis.
    """

    def menu_amis(self):
        conn = get_conn()
        amis = conn.execute(
            "SELECT username FROM friendships JOIN users ON friendships.friend_id = users.id WHERE friendships.user_id=? AND friendships.status='friends'",
            (self.Id_Utilisateur,),
        ).fetchall()
        amis += conn.execute(
            "SELECT username FROM friendships JOIN users ON friendships.user_id = users.id WHERE friendships.friend_id=? AND friendships.status='friends'",
            (self.Id_Utilisateur,),
        ).fetchall()
        conn.close()

        friends_menu = FriendsMenu()
        friends_menu.ids.liste_amis.clear_widgets()
        for row in amis:
            friends_menu.ids.liste_amis.add_widget(ListItemAmis(username=row[0]))

        self.dialog = MDDialog(
            title="Amis",
            type="custom",
            content_cls=friends_menu,
            md_bg_color=self.background,
        )
        self.dialog.open()

    def menu_demande_amis(self):
        self.dialog.dismiss()

        demande_amis_content = DemandeAmis()
        liste_demandes = recuperer_demandes_amis(self.Id_Utilisateur)
        demande_amis_content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            demande_amis_content.ids.liste_demandes.add_widget(
                ListItemDemandeAmis(username=username)
            )

        self.dialog = MDDialog(
            title="Demandes",
            type="custom",
            content_cls=demande_amis_content,
            md_bg_color=self.background,
        )
        self.dialog.open()

    def refresh_demandes(self):
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, DemandeAmis):
            return

        liste_demandes = recuperer_demandes_amis(self.Id_Utilisateur)
        content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            content.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=username))

    def refresh_amis(self):
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, FriendsMenu):
            return

        conn = get_conn()
        amis = conn.execute(
            "SELECT username FROM friendships JOIN users ON friendships.friend_id = users.id WHERE friendships.user_id=? AND friendships.status='friends'",
            (self.Id_Utilisateur,),
        ).fetchall()
        amis += conn.execute(
            "SELECT username FROM friendships JOIN users ON friendships.user_id = users.id WHERE friendships.friend_id=? AND friendships.status='friends'",
            (self.Id_Utilisateur,),
        ).fetchall()
        conn.close()

        content.ids.liste_amis.clear_widgets()
        for row in amis:
            content.ids.liste_amis.add_widget(ListItemAmis(username=row[0]))

    def accept_request(self, username):
        conn = get_conn()
        userid_row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not userid_row:
            conn.close()
            return
        userid = userid_row[0]

        friendships = conn.execute(
            """SELECT id FROM friendships
               WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?))
               AND status='pending'""",
            (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur),
        ).fetchall()

        if friendships:
            for row in friendships:
                conn.execute("DELETE FROM friendships WHERE id=?", (row[0],))
            conn.execute(
                "INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'friends')",
                (userid, self.Id_Utilisateur),
            )
            conn.commit()

        conn.close()
        self.refresh_demandes()

    def refuse_request(self, username):
        conn = get_conn()
        userid_row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not userid_row:
            conn.close()
            return
        userid = userid_row[0]

        friendship = conn.execute(
            """SELECT id FROM friendships
               WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?))
               AND status='pending'""",
            (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur),
        ).fetchone()

        if friendship:
            conn.execute("DELETE FROM friendships WHERE id=?", (friendship[0],))
            conn.commit()

        conn.close()
        self.refresh_demandes()

    def envoyer_demande(self, username):
        conn = get_conn()
        user = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()

        if user is None:
            conn.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(title="Erreur", text=f"L'utilisateur {username} n'existe pas")
            self.dialog.open()
            return

        bonid = user[0]
        if bonid == self.Id_Utilisateur:
            conn.close()
            return

        deja = conn.execute(
            "SELECT id FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'",
            (self.Id_Utilisateur, bonid),
        ).fetchone()

        if deja:
            conn.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(title="Soucis", text="Demande déjà envoyée")
            self.dialog.open()
            return

        conn.execute(
            "INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'pending')",
            (self.Id_Utilisateur, bonid),
        )
        conn.commit()
        conn.close()

        self.dialog.dismiss()
        self.dialog = MDDialog(title="Succès", text=f"Demande envoyée à {username}")
        self.dialog.open()

    def supprimer_ami(self, username):
        conn = get_conn()
        userid_row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not userid_row:
            conn.close()
            return
        userid = userid_row[0]

        conn.execute(
            """DELETE FROM friendships
            WHERE ((user_id=? AND friend_id=?) OR (user_id=? AND friend_id=?))
            AND status='friends'""",
            (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur),
        )
        conn.commit()
        conn.close()
        self.refresh_amis()

    def voir_profil(self, username):
        pass  # à coder plus tard
