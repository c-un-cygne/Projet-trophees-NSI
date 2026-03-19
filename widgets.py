from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty


class FriendsMenu(MDBoxLayout):
    pass


class DemandeAmis(MDBoxLayout):
    pass


class ListItemDemandeAmis(MDBoxLayout):
    username = StringProperty()


class ListItemAmis(MDBoxLayout):
    username = StringProperty()


class ActivityItem(MDBoxLayout):
    activity_id       = NumericProperty(0)
    activity_name     = StringProperty()
    activity_category = StringProperty()
    activity_unit     = StringProperty()
    activity_factor   = NumericProperty(0)