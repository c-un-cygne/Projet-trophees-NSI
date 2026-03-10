from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.bottomnavigation import MDBottomNavigationItem

Window.size = [300, 600]

class LoginScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class ConnexionScreen(Screen):
    pass

class InscriptionScreen(Screen):
    pass

#pour les tabs de la bar de nav
class HomeTab(MDBottomNavigationItem):
    pass

class ProfileTab(MDBottomNavigationItem):
    pass

class AddTab(MDBottomNavigationItem):
    pass

class LeaderboardTab(MDBottomNavigationItem):
    pass

class TropheeNSIApp(MDApp):
    def build(self):
        return Builder.load_file("data/res.kv")

if __name__ == "__main__":
    TropheeNSIApp().run()