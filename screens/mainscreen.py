from kivy.uix.screenmanager import Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivy.clock import Clock
from kivymd.app import MDApp


class MainScreen(Screen):
    pass


class HomeTab(MDBottomNavigationItem):
    pass


class ProfileTab(MDBottomNavigationItem):
    pass


class LeaderboardTab(MDBottomNavigationItem):
    pass


class AddTab(MDBottomNavigationItem):
    """Onglet d'ajout d'activité carbone."""

    # Activité sélectionnée (dict avec id, name, factor, unit)
    _selected_activity = None

    # ── Recherche / filtrage ───────────────────────────────────────────────

    def on_enter(self, *args):
        """Appelé à chaque fois que l'onglet devient visible."""
        Clock.schedule_once(lambda dt: self._init_categories(), 0)

    def _init_categories(self):
        from db import get_categories
        cats = ["Toutes"] + get_categories()
        spinner = self.ids.get("category_spinner")
        if spinner:
            spinner.values = cats
            spinner.text = "Toutes"
        self.rechercher()

    def rechercher(self):
        """Rafraîchit la liste selon la recherche textuelle et la catégorie."""
        from db import rechercher_activites
        query = self.ids.search_field.text.strip()
        cat_raw = self.ids.category_spinner.text
        categorie = "" if cat_raw in ("Toutes", "") else cat_raw
        activites = rechercher_activites(query, categorie)
        self._afficher_resultats(activites)

    def _afficher_resultats(self, activites: list):
        from widgets import ActivityItem
        liste = self.ids.activities_list
        liste.clear_widgets()
        for act in activites:
            item = ActivityItem(
                activity_id=act["id"],
                activity_name=act["name"],
                activity_category=act["category"],
                activity_unit=act["unit"],
                activity_factor=act["factor"],
            )
            liste.add_widget(item)

    # ── Sélection d'une activité ───────────────────────────────────────────

    def selectionner_activite(self, activity_id, name, unit, factor):
        self._selected_activity = {
            "id": activity_id,
            "name": name,
            "unit": unit,
            "factor": factor,
        }
        self.ids.selected_label.text = f"[b]{name}[/b]  ({unit})"
        self.ids.quantity_field.disabled = False
        self.ids.valider_btn.disabled = False
        self.ids.quantity_field.hint_text = f"Quantité en {unit}"
        self.ids.quantity_field.text = ""

    # ── Validation ────────────────────────────────────────────────────────

    def valider(self):
        app = MDApp.get_running_app()
        if not self._selected_activity:
            self.ids.feedback_label.text = "Sélectionne d'abord une activité."
            return

        raw = self.ids.quantity_field.text.strip().replace(",", ".")
        try:
            quantity = float(raw)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            self.ids.feedback_label.text = "Quantité invalide (nombre > 0 requis)."
            return

        from db import ajouter_entree_carbone
        co2 = ajouter_entree_carbone(
            user_id=app.Id_Utilisateur,
            activity_id=self._selected_activity["id"],
            quantity=quantity,
        )

        self.ids.feedback_label.text = (
            f"✓ +{co2:.3f} kg CO₂ ajouté !"
        )
        self._reset_selection()

    def _reset_selection(self):
        self._selected_activity = None
        self.ids.selected_label.text = "Aucune activité sélectionnée"
        self.ids.quantity_field.text = ""
        self.ids.quantity_field.disabled = True
        self.ids.valider_btn.disabled = True
        Clock.schedule_once(lambda dt: self._clear_feedback(), 3)

    def _clear_feedback(self):
        try:
            self.ids.feedback_label.text = ""
        except Exception:
            pass