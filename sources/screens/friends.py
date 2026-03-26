#Projet : TerraGauge
#Auteurs : Léo Diotallevi, Patrick Addison, Maël Yvetot
from kivymd.uix.dialog import MDDialog
from kivy.animation import Animation

from db import get_friends_list, recuperer_demandes_amis, accept_friend_request, refuse_friend_request, send_friend_request, remove_friend
from widgets import FriendsMenu, DemandeAmis, ListItemAmis, ListItemDemandeAmis


class FriendsMixin:

    def fermer_menu(self):
        self.dialog.dismiss()

    def menu_amis(self):
        amis = get_friends_list(self.id_user)

        menu = FriendsMenu()
        menu.ids.liste_amis.clear_widgets()
        for u in amis:
            menu.ids.liste_amis.add_widget(ListItemAmis(username=u))

        self.dialog = MDDialog(
            title="Amis",
            type="custom",
            content_cls=menu,
            md_bg_color=self.background,
        )
        self.dialog.open()

    def menu_demande_amis(self):
        # petite anim pour pas que ça soit brutal
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *a: self.ouvrir_demandes())
        anim.start(self.dialog)

    def ouvrir_demandes(self):
        self.dialog.dismiss()

        contenu = DemandeAmis()
        contenu.ids.liste_demandes.clear_widgets()
        for u in recuperer_demandes_amis(self.id_user):
            contenu.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=u))

        self.dialog = MDDialog(
            title="Demandes",
            type="custom",
            content_cls=contenu,
            md_bg_color=self.background,
        )
        self.dialog.opacity = 0
        self.dialog.open()
        Animation(opacity=1, duration=0.15).start(self.dialog)

    def refresh_demandes(self):
        if not self.dialog or not isinstance(self.dialog.content_cls, DemandeAmis):
            return

        contenu = self.dialog.content_cls
        contenu.ids.liste_demandes.clear_widgets()
        for u in recuperer_demandes_amis(self.id_user):
            contenu.ids.liste_demandes.add_widget(ListItemDemandeAmis(username=u))

    def refresh_amis(self):
        if not self.dialog or not isinstance(self.dialog.content_cls, FriendsMenu):
            return

        contenu = self.dialog.content_cls
        contenu.ids.liste_amis.clear_widgets()
        for u in get_friends_list(self.id_user):
            contenu.ids.liste_amis.add_widget(ListItemAmis(username=u))

    def accept_request(self, username):
        if accept_friend_request(self.id_user, username):
            self.refresh_demandes()

    def refuse_request(self, username):
        if refuse_friend_request(self.id_user, username):
            self.refresh_demandes()

    def envoyer_demande(self, username):
        res = send_friend_request(self.id_user, username)
        self.dialog.dismiss()

        msgs = {
            "success":      f"Demande envoyée à {username} !",
            "not_found":    f"L'utilisateur '{username}' existe pas",
            "self":         "Tu peux pas t'envoyer une demande à toi-même...",
            "already_sent": "Demande déjà envoyée ou vous êtes déjà amis",
        }
        texte = msgs.get(res, "Une erreur est survenue")
        self.dialog = MDDialog(title="Amis", text=texte)
        self.dialog.open()

    def supprimer_ami(self, username):
        if remove_friend(self.id_user, username):
            self.refresh_amis()

    def voir_profil(self, username):
        pass  # à faire plus tard
