from lib.plougame import Page
from data.spec import Spec

states = ['bases']

class Offline(Page):

    def __init__(self, client):

        components = Spec.formatter.get_components('ui/data/page.json')

        super().__init__(states, components, active_states='all')

        self.add_button_logic('back', self.go_back)