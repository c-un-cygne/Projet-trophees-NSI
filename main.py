import sqlite3
import os
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, OneLineListItem
<<<<<<< HEAD
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
=======
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty
import time
>>>>>>> main

Window.size = [300, 600]

rep_base = os.path.dirname(os.path.abspath(__file__))
db_rep = os.path.join(rep_base, "data/users.db")


class LoginScreen(Screen):
    pass


class MainScreen(Screen):
    pass


class ConnexionScreen(Screen):

    def connexion(self):
        utilisateur = self.ids.utilisateur.text
        mot_de_passe = self.ids.mot_de_passe.text

        c = sqlite3.connect(db_rep)
        curseur = c.cursor()
        curseur.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (utilisateur, mot_de_passe),
        )
        resultat = curseur.fetchone()
        c.close()

        if resultat:
            MDApp.get_running_app().Id_Utilisateur = resultat[0]
            MDApp.get_running_app().root.current = "main"
        else:
            self.ids.error.text = "Nom d'utilisateur ou mot de passe incorrect"


class InscriptionScreen(Screen):

    def inscription(self):
        utilisateur = self.ids.utilisateur.text
        mot_de_passe = self.ids.mot_de_passe.text
        mot_de_passe2 = self.ids.mot_de_passe2.text

        if mot_de_passe != mot_de_passe2:
            self.ids.password_error.text = "Les mots de passe ne correspondent pas"
            return

        if len(mot_de_passe) < 6:
            self.ids.password_error.text = "Le mot de passe doit contenir au moins 6 caractères"
            return

        self.ids.password_error.text = ""

        email = self.ids.email.text

        c = sqlite3.connect(db_rep)
        curseur = c.cursor()

        curseur.execute("SELECT id FROM users WHERE username=?", (utilisateur,))
        if curseur.fetchone():
            self.ids.password_error.text = "Nom d'utilisateur déjà utilisé"
            c.close()
            return
<<<<<<< HEAD

        curseur.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (utilisateur, mot_de_passe, email),
        )
        c.commit()

        curseur.execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (utilisateur, mot_de_passe),
        )
        resultat = curseur.fetchone()
        c.close()

        MDApp.get_running_app().Id_Utilisateur = resultat[0]
        MDApp.get_running_app().root.current = "main"

=======
        curseur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (utilisateur, mot_de_passe, emails))
        c.commit()
        curseur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (utilisateur, mot_de_passe))
        resultat = curseur.fetchone()
        c.close()
        MDApp.get_running_app().Id_Utilisateur = resultat[0]
        MDApp.get_running_app().root.current = "main"
>>>>>>> main
        self.ids.utilisateur.text = ""
        self.ids.email.text = ""
        self.ids.mot_de_passe.text = ""
        self.ids.mot_de_passe2.text = ""
<<<<<<< HEAD


# Tabs de la barre de navigation
=======
#pour les tabs de la bar de nav
>>>>>>> main
class HomeTab(MDBottomNavigationItem):
    pass


class ProfileTab(MDBottomNavigationItem):
    pass


class AddTab(MDBottomNavigationItem):
    pass


class LeaderboardTab(MDBottomNavigationItem):
    pass


class FriendsMenu(MDBoxLayout):
    pass
<<<<<<< HEAD


class DemandeAmis(MDBoxLayout):
    pass


class ListItemDemandeAmis(MDBoxLayout):
    username = StringProperty()


def recuperer_demandes_amis(user_id):
    c = sqlite3.connect(db_rep)
    curseur = c.cursor()
    curseur.execute(
        """
        SELECT users.username FROM friendships
        JOIN users ON friendships.user_id = users.id
        WHERE friendships.friend_id = ? AND friendships.status = 'pending'
        """,
        (user_id,),
    )
    demandes = [i[0] for i in curseur.fetchall()]
    c.close()
    return demandes


=======
class DemandeAmis(MDBoxLayout):
    pass
class ListItemDemandeAmis(MDBoxLayout):
    username = StringProperty()

def recupérer_demandes_amis(user_id):
    c = sqlite3.connect(db_rep)
    curseur = c.cursor()
    curseur.execute("""
        SELECT users.username FROM friendships 
        JOIN users ON friendships.user_id = users.id 
        WHERE friendships.friend_id = ? AND friendships.status = 'pending'
    """, (user_id,))
    demandes = [i[0] for i in curseur.fetchall()]
    c.close()
    return demandes
>>>>>>> main
class TropheeNSIApp(MDApp):

    def build(self):
        self.primary = get_color_from_hex("#285430")
        self.secondary = get_color_from_hex("#5F8D4E")
        self.accent = get_color_from_hex("#A4BE7B")
        self.background = get_color_from_hex("#E5D9B6")

        Window.clearcolor = self.background

        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.theme_style = "Light"

        return Builder.load_file("data/res.kv")
<<<<<<< HEAD

=======
    def accept_request(self, username):
        print("Accept:", username)
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()
        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        userid = curseur.fetchone()[0]
        curseur.execute("SELECT id FROM friendships WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?)) AND status='pending'", (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur, ))
        friendship = curseur.fetchone()
        if friendship:
            for i in friendship:
                curseur.execute("DELETE FROM friendships WHERE id=?", (i,))
            curseur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'friends')", (userid, self.Id_Utilisateur, ))
            c.commit()
        c.close()
        self.refresh_demandes()
    def refuse_request(self, username):
        print("Refuse:", username)
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()
        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        userid = curseur.fetchone()[0]
        curseur.execute("SELECT id FROM friendships WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?)) AND status='pending'",(self.Id_Utilisateur, userid, userid, self.Id_Utilisateur))
        friendship = curseur.fetchone()
        if friendship:
            curseur.execute("DELETE FROM friendships WHERE id=?", (friendship[0],))
            c.commit()
        c.close()
        self.refresh_demandes()
    def refresh_demandes(self):
        """Recharge la liste des demandes dans le dialog ouvert."""
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, DemandeAmis):
            return
        
        liste_demandes = recupérer_demandes_amis(self.Id_Utilisateur)
        content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            content.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=username))
>>>>>>> main
    def menu_amis(self):
        self.dialog = MDDialog(
            title="Amis",
            type="custom",
            content_cls=FriendsMenu(),
        )
        self.dialog.open()
<<<<<<< HEAD

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
        )
        self.dialog.open()

    def refresh_demandes(self):
        """Recharge la liste des demandes dans le dialog ouvert."""
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, DemandeAmis):
            return

        liste_demandes = recuperer_demandes_amis(self.Id_Utilisateur)
        content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            content.ids.liste_demandes.add_widget(
                ListItemDemandeAmis(username=username)
            )

    def accept_request(self, username):
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()

        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        userid = curseur.fetchone()[0]

        curseur.execute(
            """SELECT id FROM friendships
               WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?))
               AND status='pending'""",
            (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur),
        )
        friendship = curseur.fetchone()

        if friendship:
            for i in friendship:
                curseur.execute("DELETE FROM friendships WHERE id=?", (i,))
            curseur.execute(
                "INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'friends')",
                (userid, self.Id_Utilisateur),
            )
            c.commit()

        c.close()
        self.refresh_demandes()

    def refuse_request(self, username):
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()

        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        userid = curseur.fetchone()[0]

        curseur.execute(
            """SELECT id FROM friendships
               WHERE ((friend_id=? AND user_id=?) OR (friend_id=? AND user_id=?))
               AND status='pending'""",
            (self.Id_Utilisateur, userid, userid, self.Id_Utilisateur),
        )
        friendship = curseur.fetchone()

        if friendship:
            curseur.execute("DELETE FROM friendships WHERE id=?", (friendship[0],))
            c.commit()

        c.close()
        self.refresh_demandes()

=======
    def menu_demande_amis(self):
        self.dialog.dismiss()
        
        demande_amis_content = DemandeAmis()
        
        liste_demandes = recupérer_demandes_amis(self.Id_Utilisateur)
        demande_amis_content.ids.liste_demandes.clear_widgets()
        
        for username in liste_demandes:
            demande_amis_content.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=username))
        
        self.dialog = MDDialog(title="Demandes", type="custom", content_cls=demande_amis_content)
        self.dialog.open()
>>>>>>> main
    def envoyer_demande(self, username):
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()

        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        user = curseur.fetchone()

        if user is None:
            c.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Erreur",
                text=f"L'utilisateur {username} n'existe pas",
            )
            self.dialog.open()
            return

        bonid = user[0]

        if bonid == self.Id_Utilisateur:
            c.close()
            return
<<<<<<< HEAD

        curseur.execute(
            "SELECT id FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'",
            (self.Id_Utilisateur, bonid),
        )

=======
        curseur.execute("SELECT id FROM friendships WHERE user_id=? AND friend_id=? AND status='pending'", (self.Id_Utilisateur, bonid))
>>>>>>> main
        if curseur.fetchone():
            c.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(
                title="Soucis",
                text="Demande déjà envoyée",
            )
            self.dialog.open()
            return

        curseur.execute(
            "INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'pending')",
            (self.Id_Utilisateur, bonid),
        )
        c.commit()
        c.close()

        self.dialog.dismiss()
        self.dialog = MDDialog(
            title="Succès",
            text=f"Demande envoyée à {username}",
        )
        self.dialog.open()


if __name__ == "__main__":
    TropheeNSIApp().run()