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
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem



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
        curseur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (utilisateur, mot_de_passe))
        resultat = curseur.fetchone()
        c.close()
        if resultat:
            MDApp.get_running_app().root.current = "main"
            MDApp.get_running_app().Id_Utilisateur = resultat[0]
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
        elif len(mot_de_passe) < 6:
            self.ids.password_error.text = "Le mot de passe doit contenir au moins 6 caractères"
            return
        self.ids.password_error.text = ""
        emails = self.ids.email.text
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()
        curseur.execute("SELECT id FROM users WHERE username=?", (utilisateur,))
        if curseur.fetchone():
            self.ids.password_error.text = "Nom d'utilisateur déjà utilisé"
            c.close()
            return
        curseur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (utilisateur, mot_de_passe, emails))
        c.commit()  
        c.close()
        self.ids.utilisateur.text = ""
        self.ids.email.text = ""
        self.ids.mot_de_passe.text = ""
        self.ids.mot_de_passe2.text = ""
        MDApp.get_running_app().root.current = "main"

#pour les tabs de la bar de nav
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
class TropheeNSIApp(MDApp):
    def build(self):
        return Builder.load_file("data/res.kv")
    def menu_amis(self):
        self.dialog = MDDialog(title="Amis", type="custom",  content_cls=FriendsMenu())
        self.dialog.open()
    def envoyer_demande(self, username):
        c = sqlite3.connect(db_rep)
        curseur = c.cursor()
        curseur.execute("SELECT id FROM users WHERE username=?", (username,))
        user = curseur.fetchone()    
        if user is None:
            c.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(title = "Erreur", text=f"L'utilsateur {username} n'existe pas")
            self.dialog.open()
            return
        bonid = user[0]
        if bonid == self.Id_Utilisateur:
            c.close()
            return
        curseur.execute("SELECT id FROM friendships WHERE user_id=? AND friend_id=? AND status=pending", (self.Id_Utilisateur, bonid))
        if curseur.fetchone():
            c.close()
            self.dialog.dismiss()
            self.dialog = MDDialog(title="Soucis", text="Demande déja envoyéé")
            self.dialog.open()
            return
        curseur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (?, ?, 'pending')", (self.Id_Utilisateur, bonid))
        c.commit()
        c.close()
        self.dialog.dismiss()
        self.dialog = MDDialog(title="Succès", text = f"Demande envoyéé à {username}")
        self.dialog.open()
        
if __name__ == "__main__":
    TropheeNSIApp().run()