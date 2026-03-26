from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex

from screens.auth import LoginScreen, ConnexionScreen, InscriptionScreen
from screens.mainscreen import MainScreen, HomeTab, ProfileTab, AddTab, LeaderboardTab
from screens.friends import FriendsMixin
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis, ActivityItem, LeaderboardRow

# taille fixe pour simuler un écran de téléphone
Window.size = (300, 600)


class TerraGaugeApp(FriendsMixin, MDApp):

    # infos de l'utilisateur connecté, vides par défaut
    pseudo = StringProperty("")
    mail = StringProperty("")
    nb_amis = StringProperty("0")
    co2_total = StringProperty("0.000")
    id_user = None

    def build(self):
        # couleurs qu'on a choisies, palette verte pour coller au thème écologie
        self.primary    = get_color_from_hex("#285430")
        self.secondary  = get_color_from_hex("#5F8D4E")
        self.accent     = get_color_from_hex("#A4BE7B")
        self.background = get_color_from_hex("#E5D9B6")

        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"

        for f in ["widgets", "auth", "main", "friends"]:
            Builder.load_file(f"ui/{f}.kv")

        kv = Builder.load_file("ui/base.kv")
        kv.transition.clearcolor = self.background
        Window.clearcolor = self.background
        return kv

    def aller_accueil(self):
        self.root.get_screen("main").ids.bottom_nav.current = "home"

    def maj_nb_amis(self):
        if not self.id_user:
            return

        from db import get_friends_count
        self.nb_amis = str(get_friends_count(self.id_user))

    def maj_co2(self):
        if not self.id_user:
            return
        from db import get_total_co2
        self.co2_total = f"{get_total_co2(self.id_user):.3f}"

    def deconnexion(self):
        self.id_user = None
        self.pseudo = ""
        self.mail = ""
        self.nb_amis = "0"
        self.co2_total = "0.000"


        # on vide les champs pour pas que ça reste affiché
        ecran_co = self.root.get_screen("connexion")
        ecran_co.ids.utilisateur.text = ""
        ecran_co.ids.mot_de_passe.text = ""
        ecran_co.ids.error.text = ""

        self.aller_accueil()
        self.root.current = "login"
