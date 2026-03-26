from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty


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


class LeaderboardRow(MDBoxLayout):
    rank        = NumericProperty(0)
    lb_username = StringProperty()
    lb_co2      = StringProperty()
    is_me       = BooleanProperty(False)