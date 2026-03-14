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
    friends_count = StringProperty("0")
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
            if hasattr(main_screen, 'ids') and hasattr(main_screen.ids, 'bottom_nav'):
                main_screen.ids.bottom_nav.current = "home"
        except Exception as e:
            print(f"Erreur go_home_tab: {e}")

    def update_friends_count(self):
        """Met à jour le nombre d'amis de l'utilisateur"""
        if self.Id_Utilisateur:
            try:
                from db import get_conn
                conn = get_conn()
                # Récupérer les amis où l'utilisateur est l'initiateur
                amis1 = conn.execute(
                    "SELECT COUNT(*) FROM friendships WHERE user_id=? AND status='friends'",
                    (self.Id_Utilisateur,),
                ).fetchone()[0]
                # Récupérer les amis où l'utilisateur est le destinataire
                amis2 = conn.execute(
                    "SELECT COUNT(*) FROM friendships WHERE friend_id=? AND status='friends'",
                    (self.Id_Utilisateur,),
                ).fetchone()[0]
                conn.close()
                self.friends_count = str(amis1 + amis2)
            except Exception:
                self.friends_count = "0"

    def deconnexion(self):
        self.Id_Utilisateur = None
        self.username = ""
        self.email = ""
        self.friends_count = "0"

        if hasattr(self, "dialog") and self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass

        if self.root:
            try:
                main_screen = self.root.get_screen("main")
                if hasattr(main_screen, 'ids') and hasattr(main_screen.ids, 'bottom_nav'):
                    main_screen.ids.bottom_nav.current = "home"
            except Exception:
                pass
            
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
