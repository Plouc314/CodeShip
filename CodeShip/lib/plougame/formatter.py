from .form import Form
from .components import TextBox, Button, InputText, ScrollList, Cadre
from .auxiliary import Font, C
from typing import List, Set, Dict, Tuple, Union
import json, re

map_class = {
    'Form': Form,
    'Cadre': Cadre,
    'TextBox': TextBox,
    'Button': Button,
    'InputText': InputText,
    'ScrollList': ScrollList,
}

class Formatter:
    '''
    Formatter used to process JSON-like files.
    '''

    def __init__(self):
        self._templates = {}

    def get_color(self, string: str) -> tuple:
        '''
        Return a tuple of the color given a string.  
        Will format the string to the variables name's format
        and look if the color exist in `C`, if not raise an error.
        '''
        format_string = string.replace(' ', '_').upper()
        
        assert hasattr(C, format_string), f'Unknow color: "{string}"'

        return getattr(C, format_string)

    def _handeln_template(self, data: dict) -> dict:
        '''
        Handeln potential template(s).  
        Check if a template is specified,
        if so and template unknow: raise an error,
        else merge template and given data.
        '''
        if not 'template' in data.keys() and not 'templates' in data.keys():
            return data

        if 'template' in data.keys():
            tpl_names = [data.pop('template')]
        else:
            tpl_names = data.pop('templates')

        template = {}

        for tpl_name in tpl_names:
            
            assert tpl_name in self._templates.keys(), f"Unknown template: '{tpl_name}'"

            # merge tamplates
            template = {**template, **self._templates[tpl_name]}

        # finally add data
        return {**template, **data}

    def get_components(self, path) -> List[Tuple]:
        '''
        Create all the components defined in the .json file of the
        given path.  
        Process the file to handeln any variables or expressions.  
        Return a list of tuples with each time a pair: name, object
        It is the same format as the `components`argument of the `Page` object.
        '''
        # load file
        with open(path, 'r') as file:
            string = file.read()

        # process string
        string = self.process_variables(string)
        string = self.evaluate_values(string)
        
        # use json decoder
        try:
            data = json.loads(string)
        except:
            raise SyntaxError("JSON decoder failed, processed file:\n"+string)

        # create components
        components = []

        for name, infos in data.items():

            assert 'type' in infos.keys(), "Each component must specify a type."

            _class = infos.pop('type')
            _class = map_class[_class]

            infos = self._process_special_attributes(infos)

            infos = self._handeln_template(infos)

            if not 'dim' in infos.keys():
                infos['dim'] = None

            component = _class(**infos)

            components.append((name, component))
        
        return components

    def process_templates(self, path):
        '''
        Process the templates
        '''
         # load file
        with open(path, 'r') as file:
            string = file.read()

        # process string
        string = self.process_variables(string)
        string = self.evaluate_values(string)
        
        # use json decoder
        data = json.loads(string)

        for name, infos in data.items():
            
            infos = self._process_special_attributes(infos)

            if name in self._templates.keys():
                # update old template with new one
                self._templates[name] = {**self._templates[name], **infos}
            else:
                # create new template
                self._templates[name] = infos

    def _process_special_attributes(self, data: dict) -> dict:
        '''
        For specific attribute extra processing is needed,  
        it is executed here.  
        Return the processed data
        '''
        if 'font' in data.keys():
            data['font'] = Font.f(data['font'])

        if 'color' in data.keys():
            data['color'] = self.get_color(data['color'])
        
        if 'text_color' in data.keys():
            data['text_color'] = self.get_color(data['text_color'])

        return data

    def process_variables(self, string: str):
        '''
        Identify and subsitute variables by their value.  
        '''
        # var_data is a list of (variable name, value)
        var_data = re.findall('([a-zA-Z0-9_]+)\s?=\s?(.+)', string)

        # select part of string that contains the json data
        match = re.search('^\{', string, flags=re.MULTILINE)
        idx = match.span()[0]
        string = string[idx:]

        for name, value in var_data:
            while name in string:
                string = string.replace(name, value)
        
        return string.strip()
        
    def evaluate_values(self, string: str):
        '''
        Evaluate each value of the .json file,
        return a readable string for the json module.  
        Must be executed after `process_variables`.
        '''
        expressions = re.findall('.+:\s?([^{[\n]+)', string)

        for exp in expressions:
            
            # get rid of null exp (by ex. the dicts)
            if not exp.strip():
                continue
            
            # remove potential coma at the end
            if exp[-1] == ',':
                exp = exp[:-1]

            # don't evaluate boolean values
            if exp == 'true' or exp == 'false':
                continue

            try:
                evaluated = eval(exp)
            except:
                raise ValueError(f"Couldn't evaluate expression: '{exp}'")

            if type(evaluated) == str:
                string = string.replace(exp, f'"{evaluated}"')
            else:
                string = string.replace(exp, str(evaluated))

        return string