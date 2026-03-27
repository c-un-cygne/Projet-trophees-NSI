#Projet : TerraGauge
#Auteurs : Léo Diotallevi, Patrick Addison, Maël Yvetot
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.app import MDApp
import bcrypt
from db import get_conn


class LoginScreen(Screen):
    pass


class ConnexionScreen(Screen):

    def connexion(self):
        pseudo = self.ids.utilisateur.text
        mdp = self.ids.mot_de_passe.text

        # on cherche l'utilisateur dans la bdd
        conn = get_conn()
        res = conn.execute(
            "SELECT id, email, password FROM users WHERE username = ?",
            (pseudo,)
        ).fetchone()
        conn.close()

        if not res:
            self.ids.error.text = "Utilisateur introuvable"
            return

        # bcrypt compare le mdp entré avec le hash stocké
        if not bcrypt.checkpw(mdp.encode(), res[2].encode()):
            self.ids.error.text = "Mot de passe incorrect"
            return

        app = MDApp.get_running_app()
        app.id_user = res[0]
        app.pseudo = pseudo
        app.mail = res[1]
        app.maj_nb_amis()
        app.root.current = "main"
        # petit délai sinon l'onglet home se charge pas bien
        Clock.schedule_once(lambda dt: app.aller_accueil(), 1.0)
        app.root.get_screen("main").ids.bottom_nav.ids.tab_manager.get_screen("home").maj_accueil()


class InscriptionScreen(Screen):

    def inscription(self):
        pseudo = self.ids.utilisateur.text.strip()
        mdp = self.ids.mot_de_passe.text
        mdp2 = self.ids.mot_de_passe2.text
        email = self.ids.email.text.strip()

        if mdp != mdp2:
            self.ids.password_error.text = "Les mots de passe ne correspondent pas "
            return

        if len(mdp) < 6:
            self.ids.password_error.text = "Minimum 6 caractères pour le mot de passe"
            return

        self.ids.password_error.text = ""

        conn = get_conn()

        # on vérifie que le pseudo est dispo
        deja_pris = conn.execute(
            "SELECT id FROM users WHERE username=?", (pseudo,)
        ).fetchone()
        if deja_pris:
            self.ids.password_error.text = "Ce pseudo est déjà pris"
            conn.close()
            return

        hash_mdp = bcrypt.hashpw(mdp.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (pseudo, hash_mdp, email)
        )
        conn.commit()

        # on récupère l'id qu'on vient de créer
        nouvel_id = conn.execute(
            "SELECT id FROM users WHERE username=?", (pseudo,)
        ).fetchone()[0]
        conn.close()

        app = MDApp.get_running_app()
        app.id_user = nouvel_id
        app.pseudo = pseudo
        app.mail = email
        app.maj_nb_amis()
        app.root.current = "main"
        Clock.schedule_once(lambda dt: app.aller_accueil(), 1.0)

        # on vide les champs
        self.ids.utilisateur.text = ""
        self.ids.email.text = ""
        self.ids.mot_de_passe.text = ""
        self.ids.mot_de_passe2.text = ""
