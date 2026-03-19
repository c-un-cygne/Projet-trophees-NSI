from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.clock import Clock
from kivymd.app import MDApp


class MainScreen(Screen):
    pass


class HomeTab(MDBottomNavigationItem):
    pass


class LeaderboardTab(MDBottomNavigationItem):
    pass


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
        # on attend un peu avant de lancer la recherche pour ne pas
        # envoyer une requête à chaque lettre tapée
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