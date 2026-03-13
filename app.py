from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex

# Screens
from screens.auth import LoginScreen, ConnexionScreen, InscriptionScreen
from screens.mainscreen import MainScreen, HomeTab, ProfileTab, AddTab, LeaderboardTab
from screens.friends import FriendsMixin

# Widgets personnalisés (doivent être importés pour que Kivy les reconnaisse dans les KV)
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis


Window.size = [300, 600]


class TerraGaugeApp(FriendsMixin, MDApp):
    username = StringProperty("")
    email = StringProperty("")
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

        # Chargement de tous les fichiers KV
        for kv_file in ["widgets", "auth", "main", "friends"]:
            Builder.load_file(f"ui/{kv_file}.kv")

        kv = Builder.load_file("ui/base.kv")
        kv.transition.clearcolor = self.background
        Window.clearcolor = self.background
        return kv

    def go_home_tab(self):
        try:
            main_screen = self.root.get_screen("main")
            main_screen.ids.bottom_nav.current = "home"
        except Exception:
            pass

    def deconnexion(self):
        self.Id_Utilisateur = None
        self.username = ""
        self.email = ""

        if hasattr(self, "dialog") and self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass

        if self.root:
            try:
                connexion_screen = self.root.get_screen("connexion")
                connexion_screen.ids.utilisateur.text = ""
                connexion_screen.ids.mot_de_passe.text = ""
                connexion_screen.ids.error.text = ""
            except Exception:
                pass

            try:
                main_screen = self.root.get_screen("main")
                main_screen.ids.bottom_nav.current = "home"
            except Exception:
                pass

            self.root.current = "login"
