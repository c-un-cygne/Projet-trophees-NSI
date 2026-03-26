#Projet : TerraGauge
#Auteurs : Léo Diotallevi, Patrick Addison, Maël Yvetot
from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.clock import Clock
from kivymd.app import MDApp


class MainScreen(Screen):
    pass


class HomeTab(MDBottomNavigationItem):
    MOYENNE_FR = 77

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        if app.id_user:
            self.maj_accueil()

    def maj_accueil(self):
        from db import get_co2_semaine
        app = MDApp.get_running_app()
        co2 = get_co2_semaine(app.id_user)
        self.ids.label_co2_semaine.text = f"{co2:.1f} kg CO2 cette semaine"

        diff = self.MOYENNE_FR - co2

        if co2 == 0:
            self.ids.label_message.text = "T'as rien enregistré cette semaine !"
        elif diff > 10:
            self.ids.label_message.text = f"Bien joué, t'es {diff:.1f} kg sous la moyenne 🌱"
        elif diff > 0:
            self.ids.label_message.text = f"Presque, encore {diff:.1f} kg à économiser"
        else:
            self.ids.label_message.text = f"Aïe, {abs(diff):.1f} kg au dessus de la moyenne française..."


class LeaderboardTab(MDBottomNavigationItem):

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        if app.id_user:
            self.charger_classement()

    def charger_classement(self, t=False):
        from db import get_conn, get_total_co2
        app = MDApp.get_running_app()

        conn = get_conn()

        # la table friendships est pas symétrique donc on fait deux requêtes
        amis = conn.execute(
            """SELECT users.id, users.username FROM friendships
               JOIN users ON friendships.friend_id = users.id
               WHERE friendships.user_id=? AND friendships.status='friends'""",
            (app.id_user,)
        ).fetchall()

        amis += conn.execute(
            """SELECT users.id, users.username FROM friendships
               JOIN users ON friendships.user_id = users.id
               WHERE friendships.friend_id=? AND friendships.status='friends'""",
            (app.id_user,)
        ).fetchall()

        conn.close()

        tous = [(app.id_user, app.pseudo)] + list(amis)

        # parfois le même ami apparaît deux fois à cause des deux requêtes
        vus = set()
        participants = []
        for uid, uname in tous:
            if uid in vus:
                continue
            vus.add(uid)
            participants.append((uid, uname))

        scores = []
        for uid, uname in participants:
            scores.append((uid, uname, get_total_co2(uid, t)))

        scores.sort(key=lambda x: x[2])  # moins de co2 = mieux

        self.ids.leaderboard_list.data = [
            {
                "rank": i + 1,
                "lb_username": uname,
                "lb_co2": f"{co2:.3f}",
                "is_me": uid == app.id_user,
            }
            for i, (uid, uname, co2) in enumerate(scores)
        ]


class ProfileTab(MDBottomNavigationItem):

    def on_enter(self, *args):
        MDApp.get_running_app().maj_co2()


class AddTab(MDBottomNavigationItem):

    activite_selectionnee = None
    recherche_event = None

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: self.charger_categories(), 0)

    def charger_categories(self):
        from db import get_categories
        cats = ["Toutes"] + get_categories()
        self.ids.category_spinner.values = cats
        self.ids.category_spinner.text = "Toutes"
        self.rechercher()

    def rechercher(self):
        # on annule l'event précédent pour pas spammer la bdd
        if self.recherche_event:
            self.recherche_event.cancel()
        self.recherche_event = Clock.schedule_once(lambda dt: self.faire_recherche(), 0.3)

    def faire_recherche(self):
        from db import rechercher_activites
        q = self.ids.search_field.text.strip()
        cat = self.ids.category_spinner.text
        if cat == "Toutes":
            cat = ""

        self.ids.activities_list.data = [
            {
                "activity_id": a["id"],
                "activity_name": a["name"],
                "activity_category": a["category"],
                "activity_unit": a["unit"],
                "activity_factor": a["factor"],
            }
            for a in rechercher_activites(q, cat)
        ]

    def selectionner_activite(self, activity_id, nom, unite, facteur):
        self.activite_selectionnee = {"id": activity_id, "nom": nom, "unite": unite, "facteur": facteur}
        self.ids.selected_label.text = f"[b]{nom}[/b]  ({unite})"
        self.ids.quantity_field.disabled = False
        self.ids.quantity_field.hint_text = f"Quantité en {unite}"
        self.ids.quantity_field.text = ""
        self.ids.valider_btn.disabled = False

    def valider(self):
        app = MDApp.get_running_app()

        if not self.activite_selectionnee:
            self.ids.feedback_label.text = "Sélectionne d'abord une activité."
            return

        texte = self.ids.quantity_field.text.strip().replace(",", ".")

        try:
            qte = float(texte)
            if qte <= 0:
                raise ValueError
        except ValueError:
            self.ids.feedback_label.text = "Quantité invalide."
            return

        from db import ajouter_entree_carbone
        co2 = ajouter_entree_carbone(app.id_user, self.activite_selectionnee["id"], qte)
        self.ids.feedback_label.text = f"✓ +{co2:.3f} kg CO2 ajouté !"
        app.maj_co2()
        self.reset_selection()

    def reset_selection(self):
        self.activite_selectionnee = None
        self.ids.selected_label.text = "Aucune activité sélectionnée"
        self.ids.quantity_field.text = ""
        self.ids.quantity_field.disabled = True
        self.ids.valider_btn.disabled = True
        Clock.schedule_once(lambda dt: self.effacer_feedback(), 3)

    def effacer_feedback(self):
        self.ids.feedback_label.text = ""
