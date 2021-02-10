import numpy as np
import json, os
from lib.plougame.auxiliary import C
from lib.plougame import Formatter

class Spec:
    '''
    Static object

    Store all constants variables used in the whole program (on local).
    Store the "json data", the values stored in "data.json".

    Methods
    ---
    `load`: Load all the data, performed once during import  
    `set_json_variable`: Set the value of a json data variable  
    `set_attribute`: Set the value of a constant variable.
    '''

    formatter: Formatter

    @classmethod
    def load(cls):
        '''
        Load the variable from the json file
        '''
        cls.formatter = Formatter({'C':C})
        
        cls.formatter.process_variables(os.path.join('data','spec.json'))

        # store the attirutes as a dict -> simpler to store
        cls._data = cls.formatter.get_variables()

        for name, value in cls._data.items():
            setattr(cls, name, value)
        
        # load json data
        with open(os.path.join("data","data.json"), 'r') as file:
            cls.JSON_DATA = json.load(file)

    @classmethod
    def set_json_variable(cls, name: str, value, update_json=True):
        '''
        Set the value of one of the json data's variables,  
        if update_json=True, update the `data.json` file.
        '''
        cls.JSON_DATA[name] = value

        if update_json:
            with open(os.path.join('data','data.json'), 'w') as file:
                json.dump(cls.JSON_DATA, file, indent=4)

    @classmethod
    def set_attribute(cls, name: str, value, update_json=True):
        '''
        Set the value of one of the attribute,  
        if update_json=True, update the `spec.json` file.
        '''
        setattr(cls, name, value)

        cls._data[name] = value

        if update_json:
            with open(os.path.join('data','spec.json'), 'w') as file:
                json.dump(cls._data, file, indent=4)

    @classmethod
    def update_local_profil(cls, username, client):
        '''
        Update the profil stored in local,
        updathe .json file.
        '''
        filename = os.path.join('data','accounts',f'{username}.json')
        
        with open(filename, 'w') as file:
            json.dump({
                'username': username,
                'script status': client.in_data['scst'],
                'ship status': client.in_data['shst'],
                'ship': client.in_data['sh'].tolist(),
                'script': client.in_data['sc'].split('\n')
            }, file, indent=4)

    
Spec.load()