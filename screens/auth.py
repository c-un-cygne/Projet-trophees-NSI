from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.app import MDApp
import bcrypt
from db import get_conn


class LoginScreen(Screen):
    pass


class ConnexionScreen(Screen):

    def connexion(self):
        utilisateur = self.ids.utilisateur.text
        mot_de_passe = self.ids.mot_de_passe.text

        conn = get_conn()
        resultat = conn.execute(
            "SELECT id, email, password FROM users WHERE username = ?",
            (utilisateur,),
        ).fetchone()
        conn.close()

        if resultat and bcrypt.checkpw(mot_de_passe.encode("utf-8"), resultat[2].encode("utf-8")):
            id, email, _ = resultat
            app = MDApp.get_running_app()
            app.Id_Utilisateur = id
            app.username = utilisateur
            app.email = email
            app.update_friends_count()
            app.root.current = "main"
            Clock.schedule_once(lambda dt: app.go_home_tab(), 1.0)
        else:
            self.ids.error.text = "Nom d'utilisateur ou mot de passe incorrect"


class InscriptionScreen(Screen):

    def inscription(self):
        utilisateur = self.ids.utilisateur.text
        mot_de_passe = self.ids.mot_de_passe.text
        mot_de_passe2 = self.ids.mot_de_passe2.text

        if mot_de_passe != mot_de_passe2:
            self.ids.password_error.text = "Les mots de passe ne correspondent pas (mets tes lunettes la prochaine fois)"
            return

        if len(mot_de_passe) < 6:
            self.ids.password_error.text = "Le mot de passe doit contenir au moins 6 caractères (j'ai oublié de te le dire avant, sorry)"
            return

        self.ids.password_error.text = ""
        email = self.ids.email.text
        hash_mdp = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt())
        hash_mdp_str = hash_mdp.decode("utf-8")
        conn = get_conn()
        existing = conn.execute(
            "SELECT id FROM users WHERE username=?", (utilisateur,)
        ).fetchone()
        if existing:
            self.ids.password_error.text = "Nom d'utilisateur déjà utilisé"
            conn.close()
            return

        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (utilisateur, hash_mdp_str, email),
        )
        conn.commit()

        resultat = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (utilisateur,),
        ).fetchone()
        conn.close()

        app = MDApp.get_running_app()
        app.Id_Utilisateur = resultat[0]
        app.username = utilisateur
        app.email = email
        app.update_friends_count()
        app.root.current = "main"
        Clock.schedule_once(lambda dt: app.go_home_tab(), 1.0)

        self.ids.utilisateur.text = ""
        self.ids.email.text = ""
        self.ids.mot_de_passe.text = ""
        self.ids.mot_de_passe2.text = ""
