from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex

from screens.auth import LoginScreen, ConnexionScreen, InscriptionScreen
from screens.mainscreen import MainScreen, HomeTab, ProfileTab, AddTab, LeaderboardTab
from screens.friends import FriendsMixin
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis, ActivityItem

Window.size = [300, 600]


class TerraGaugeApp(FriendsMixin, MDApp):
    username = StringProperty("")
    email = StringProperty("")
    friends_count = StringProperty("0")
    total_co2 = StringProperty("0.000")
    Id_Utilisateur = None

    def build(self):
        self.primary    = get_color_from_hex("#285430")
        self.secondary  = get_color_from_hex("#5F8D4E")
        self.accent     = get_color_from_hex("#A4BE7B")
        self.background = get_color_from_hex("#E5D9B6")

        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue     = "800"
        self.theme_cls.accent_palette  = "Green"
        self.theme_cls.theme_style     = "Light"

        for kv_file in ["widgets", "auth", "main", "friends"]:
            Builder.load_file(f"ui/{kv_file}.kv")

        kv = Builder.load_file("ui/base.kv")
        kv.transition.clearcolor = self.background
        Window.clearcolor = self.background
        return kv

    def go_home_tab(self):
        try:
            self.root.get_screen("main").ids.bottom_nav.current = "home"
        except Exception as e:
            print(f"go_home_tab erreur: {e}")

    def update_friends_count(self):
        if not self.Id_Utilisateur:
            return
        try:
            from db import get_friends_count
            count = get_friends_count(self.Id_Utilisateur)
            self.friends_count = str(count)
        except Exception:
            self.friends_count = "0"

    def update_total_co2(self):
        if not self.Id_Utilisateur:
            return
        try:
            from db import get_total_co2
            total = get_total_co2(self.Id_Utilisateur)
            self.total_co2 = f"{total:.3f}"
        except Exception:
            self.total_co2 = "0.000"

    def deconnexion(self):
        self.Id_Utilisateur = None
        self.username = ""
        self.email = ""
        self.friends_count = "0"
        self.total_co2 = "0.000"

        if hasattr(self, "dialog") and self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass

        if self.root:
            try:
                self.root.get_screen("connexion").ids.utilisateur.text = ""
                self.root.get_screen("connexion").ids.mot_de_passe.text = ""
                self.root.get_screen("connexion").ids.error.text = ""
            except Exception:
                pass
            try:
                self.root.get_screen("main").ids.bottom_nav.current = "home"
            except Exception:
                pass
            self.root.current = "login"