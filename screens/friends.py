from kivymd.uix.dialog import MDDialog

from db import get_conn, get_friends_list, recuperer_demandes_amis, accept_friend_request, refuse_friend_request, send_friend_request, remove_friend
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis
from kivy.animation import Animation

class FriendsMixin:
    """
    Mixin à hériter par TerraGaugeApp.
    Regroupe toute la logique liée aux amis.
    """
    def fermer_menu(self):
        if hasattr(self, "dialog") and self.dialog:
            try:
                self.dialog.dismiss()
            except Exception:
                pass
    

    def menu_amis(self):
        # Requête unique au lieu de deux
        amis = get_friends_list(self.Id_Utilisateur)

        friends_menu = FriendsMenu()
        friends_menu.ids.liste_amis.clear_widgets()
        for username in amis:
            friends_menu.ids.liste_amis.add_widget(ListItemAmis(username=username))

        self.dialog = MDDialog(
            title="Amis",
            type="custom",
            content_cls=friends_menu,
            md_bg_color=self.background,
        )
        self.dialog.open()

    def menu_demande_amis(self):
        
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *a: self.ouvrir_demandes())
        anim.start(self.dialog)    
    def ouvrir_demandes(self):
        self.dialog.dismiss()

        demande_amis_content = DemandeAmis()
        liste_demandes = recuperer_demandes_amis(self.Id_Utilisateur)
        demande_amis_content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            demande_amis_content.ids.liste_demandes.add_widget(
                ListItemDemandeAmis(username=username)
            )

        self.dialog = MDDialog(
            title="Demandes",
            type="custom",
            content_cls=demande_amis_content,
            md_bg_color=self.background,
        )
        self.dialog.opacity = 0
        self.dialog.open()
        Animation(opacity=1, duration=0.15).start(self.dialog)

    def refresh_demandes(self):
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, DemandeAmis):
            return

        liste_demandes = recuperer_demandes_amis(self.Id_Utilisateur)
        content.ids.liste_demandes.clear_widgets()
        for username in liste_demandes:
            content.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=username))

    def refresh_amis(self):
        if not self.dialog or not self.dialog.content_cls:
            return
        content = self.dialog.content_cls
        if not isinstance(content, FriendsMenu):
            return

        # Requête unique au lieu de deux
        amis = get_friends_list(self.Id_Utilisateur)

        content.ids.liste_amis.clear_widgets()
        for username in amis:
            content.ids.liste_amis.add_widget(ListItemAmis(username=username))

    def accept_request(self, username):
        if accept_friend_request(self.Id_Utilisateur, username):
            self.refresh_demandes()

    def refuse_request(self, username):
        if refuse_friend_request(self.Id_Utilisateur, username):
            self.refresh_demandes()

    def envoyer_demande(self, username):
        result = send_friend_request(self.Id_Utilisateur, username)
        
        self.dialog.dismiss()
        
        if result == "success":
            self.dialog = MDDialog(title="Succès", text=f"Demande envoyée à {username}")
        elif result == "not_found":
            self.dialog = MDDialog(title="Erreur", text=f"L'utilisateur {username} n'existe pas")
        elif result == "self":
            self.dialog = MDDialog(title="Erreur", text="Tu ne peux pas t'envoyer une demande à toi-même")
        elif result == "already_sent":
            self.dialog = MDDialog(title="Soucis", text="Demande déjà envoyée ou vous êtes déjà amis")
        else:
            self.dialog = MDDialog(title="Erreur", text="Une erreur est survenue")
        
        self.dialog.open()

    def supprimer_ami(self, username):
        if remove_friend(self.Id_Utilisateur, username):
            self.refresh_amis()

    def voir_profil(self, username):
        pass  # à coder plus tard
