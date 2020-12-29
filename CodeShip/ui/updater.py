import requests, json, threading
from lib.plougame import SubPage, Form, TextBox, ScrollList, InputText, Button, Cadre, Font, C
from data.spec import Spec
from lib.counter import Counter

class Updater:

    root_link = "https://raw.githubusercontent.com/Plouc314/CodeShip/master/CodeShip/"

    def load_data(self):
        '''
        Load the json data from github.
        '''
        data = requests.get(self.root_link + "data/data.json").text
        self.data = json.loads(data)

    def is_outdated(self):
        '''
        Return if the local game is an outdated version
        (if an update has been released).
        '''
        with open('data/data.json', 'r') as file:
            self.local_data = json.load(file)
        
        return self.local_data['version'] != self.data['version']

    def update(self):
        '''
        Download and replace every file by the new version one.  
        In a separated thread.
        '''
        self.thread = threading.Thread(target=self._udpate)
        self.thread.start()

    @Counter.add_func
    def _udpate(self):
        '''
        Actual implementation of `update`,
        which only call `_update` in a separated thread.
        '''
        for filename in self.local_data['files']:

            if '.png' in filename:
                response = requests.get(self.root_link + filename)
                
                if response.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(response.content)
            
            else:
                file_scr = requests.get(self.root_link + filename).text
                with open(filename, 'w') as file:
                    file.write(file_scr)
