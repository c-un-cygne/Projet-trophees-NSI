from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.clock import Clock
from kivymd.app import MDApp


class MainScreen(Screen):
    pass


class HomeTab(MDBottomNavigationItem):
    pass


class LeaderboardTab(MDBottomNavigationItem):

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        if app.Id_Utilisateur:
            self.charger_classement()

    def charger_classement(self):
        from db import get_conn, get_total_co2
        app = MDApp.get_running_app()

        if not app.Id_Utilisateur:
            return

        conn = get_conn()

        amis = conn.execute(
            """SELECT users.id, users.username FROM friendships
               JOIN users ON friendships.friend_id = users.id
               WHERE friendships.user_id=? AND friendships.status='friends'""",
            (app.Id_Utilisateur,),
        ).fetchall()
        amis += conn.execute(
            """SELECT users.id, users.username FROM friendships
               JOIN users ON friendships.user_id = users.id
               WHERE friendships.friend_id=? AND friendships.status='friends'""",
            (app.Id_Utilisateur,),
        ).fetchall()
        conn.close()

        tous = [(app.Id_Utilisateur, app.username)] + list(amis)

        # dédoublonnage au cas où
        ids_vus = set()
        participants = []
        for uid, uname in tous:
            if uid not in ids_vus:
                ids_vus.add(uid)
                participants.append((uid, uname))

        classement = []
        for uid, uname in participants:
            classement.append({
                "uid": uid,
                "username": uname,
                "co2": get_total_co2(uid)
            })

        classement.sort(key=lambda x: x["co2"])
        self.ids.leaderboard_list.data = [
            {
                "rank": i + 1,
                "lb_username": entry["username"],
                "lb_co2": f"{entry['co2']:.3f}",
                "is_me": entry["uid"] == app.Id_Utilisateur,
            }
            for i, entry in enumerate(classement)
        ]


class ProfileTab(MDBottomNavigationItem):

    def on_enter(self, *args):
        app = MDApp.get_running_app()
        app.update_total_co2()


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
        if self.recherche_event:
            self.recherche_event.cancel()
        self.recherche_event = Clock.schedule_once(lambda dt: self.faire_recherche(), 0.3)

    def faire_recherche(self):
        from db import rechercher_activites
        query = self.ids.search_field.text.strip()
        cat = self.ids.category_spinner.text
        if cat == "Toutes":
            cat = ""
        resultats = rechercher_activites(query, cat)
        self.ids.activities_list.data = [
            {
                "activity_id": a["id"],
                "activity_name": a["name"],
                "activity_category": a["category"],
                "activity_unit": a["unit"],
                "activity_factor": a["factor"],
            }
            for a in resultats
        ]

    def selectionner_activite(self, activity_id, name, unit, factor):
        self.activite_selectionnee = {
            "id": activity_id,
            "name": name,
            "unit": unit,
            "factor": factor,
        }
        self.ids.selected_label.text = f"[b]{name}[/b]  ({unit})"
        self.ids.quantity_field.disabled = False
        self.ids.quantity_field.hint_text = f"Quantité en {unit}"
        self.ids.quantity_field.text = ""
        self.ids.valider_btn.disabled = False

    def valider(self):
        app = MDApp.get_running_app()

        if not self.activite_selectionnee:
            self.ids.feedback_label.text = "Sélectionne d'abord une activité."
            return

        texte = self.ids.quantity_field.text.strip().replace(",", ".")
        try:
            quantite = float(texte)
            if quantite <= 0:
                raise ValueError
        except ValueError:
            self.ids.feedback_label.text = "Quantité invalide."
            return

        from db import ajouter_entree_carbone
        co2 = ajouter_entree_carbone(app.Id_Utilisateur, self.activite_selectionnee["id"], quantite)
        self.ids.feedback_label.text = f"✓ +{co2:.3f} kg CO2 ajouté !"
        self.reset_selection()

    def reset_selection(self):
        self.activite_selectionnee = None
        self.ids.selected_label.text = "Aucune activité sélectionnée"
        self.ids.quantity_field.text = ""
        self.ids.quantity_field.disabled = True
        self.ids.valider_btn.disabled = True
        Clock.schedule_once(lambda dt: self.effacer_feedback(), 3)

    def effacer_feedback(self):
        try:
            self.ids.feedback_label.text = ""
        except Exception:
            pass