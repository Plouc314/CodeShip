from .form import Form
from .components import TextBox, Button, InputText, ScrollList, Cadre
from .auxiliary import Font, C
from typing import List, Set, Dict, Tuple, Union
import numpy as np
import warnings, json, re, importlib, inspect

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
    Formatter used to process JSON files.  

    The aim of the formatter is to create the components of a Page object
    given one (or more) JSON files.

    In all the various type JSON files (variables, templates, components),
    each value can be a python expression, if the value is a string starting by "$".  
    For example: `"name": "$'Bob' + ' ' + 'Pol'"` is equivalent to `"name": "Bob Pol"`.  
    The lists are handled as numpy arrays: `"$[20,30] + [10,10]"` is the same as `[30,40]`.  
    To use libraries in the expressions, a "imports" key can be specified, it will contain
    a list of the libraries' names, example:  
    ```
    "imports": [
        "math",
        "numpy"
    ]
    ```


    Methods
    ---
    `get_components`: Create components for Page object from JSON file  
    `process_templates`: Process & store templates for later use from JSON file  
    `process_variables`: Process & store variables for later use from JSON file  
    `set_variables`: Set new variables in cache  
    `get_variables`: get variables cache  
    `clear`: Clear variables cache
    '''

    def __init__(self, variables: dict=None):
        self._templates = {}
        
        if variables is None:
            self._vars = {}
        else:
            self._vars = variables

    def set_variables(self, variables: dict):
        '''
        Set new variables in the Formatter cache.  
        It won't erase any existing variables but rather
        updating the existing ones and create new ones.
        
        To clear the variables cache, call the `clear` method.
        '''
        self._add_new_vars(variables)

    def get_variables(self) -> dict:
        '''
        Return the variables cache of the Formatter. (dict)
        '''
        return self._vars.copy()

    def clear(self):
        '''
        Clear the variables cache.
        '''
        self._vars = {}

    def get_components(self, path) -> List[Tuple]:
        '''
        Create all the components defined in the JSON file of the
        given path.  
        
        Each component must specify a "type" key, with its class name or its class,  
        for example, to create a TextBox object: `"type": "TextBox"`  
        to create a custom object of class "Foo", you have to import it first (in "imports"
        key, see `Formatter` doc), and then: `"type": "$Foo"`  

        Can use variables (see `process_variables` doc) and
        templates (see `process_templates` doc).  
        Variables can also be defined in the same JSON file by defining a `"vars"` entry (dict).

        Return
        ---
        A list of tuples with each time a pair: (name, object)
        It is the same format as the `components` argument of the `Page` object.

        Example
        ---
        With the template "test-like" and variable `font_size` defined previously,  
        `title = TextBox(dim, [100, 50], text="Example", color=C.LIGHT_BLUE, 
        font=Font.f(font_size))`  
        is equivalent as: 
        ```
        {
            "title": {
                "type": "TextBox",
                "template": "text-like",
                "pos": [100, 50],
                "text": "Example",
                "font": "$font_size",
                "color": "light blue"
            }
        }
        ```

        '''
        # load file
        with open(path, 'r') as file:
            data = json.load(file)

        # process variables/imports
        self._handeln_imports(data)
        self._handeln_variables(data)

        # create components
        components = []

        for name, infos in data.items():

            infos = self._handeln_template(infos, name=name)

            assert 'type' in infos.keys(), "Each component must specify a type."

            self._process_expressions(infos, name=name)

            _class = infos.pop('type')

            # handeln custom classes
            if inspect.isclass(_class):
                pass
            else:
                _class = map_class[_class]

            infos = self._process_special_attributes(infos)

            # create the component
            try:
                component = _class(**infos)
            except TypeError as e:
                raise TypeError(self._get_error('attribute', str(e), name))

            components.append((name, component))
        
        return components

    def process_templates(self, path):
        '''
        Process & store the templates of the file at the given path.  
        
        A template is a set of predefined attributes that can then
        be used to simplify the creation of component.

        Variables can also be defined in the file, by defining a `"vars"` entry
        (see `process_variables` doc).

        Here is an example of a template ("template 1") that define
        the color and dimension attributes.
        ```
        {
            "template 1": {
                "color": "blue",
                "dim": [200, 60]
            }
        }
        ```
        '''
        # load file
        with open(path, 'r') as file:
            data = json.load(file)
        
        # process variables/imports
        self._handeln_imports(data)
        self._handeln_variables(data)
        
        for name, infos in data.items():
            
            self._process_expressions(infos, name=name)

            if name in self._templates.keys():
                # update old template with new one
                self._templates[name] = {**self._templates[name], **infos}
            else:
                # create new template
                self._templates[name] = infos

    def process_variables(self, path):
        '''
        Process & store the variables of the file at the given path.

        Once defined, a variable can be used to set any attribute,
        to use it, just write `"$variable_name"`. It can also be used
        in an expression, `"$ 23 + variable_name"`.

        Example:
        ```
        {
            "var1": 20,
            "var2": [30, 120],
            "var3": "$var1 - 10",
            "var4": "$ [10, 10] + var2"
        }
        ```
        '''
        # load file
        with open(path, 'r') as file:
            data = json.load(file)

        self._handeln_imports(data)
        self._process_expressions(data)
        self._add_new_vars(data)

    def _get_color(self, string: str) -> tuple:
        '''
        Return a tuple of the color given a string.  
        Will format the string to the variables name's format
        and look if the color exist in `C`, if not raise an error.
        '''
        format_string = string.replace(' ', '_').upper()
        
        assert hasattr(C, format_string), f'Unknow color: "{string}"'

        return getattr(C, format_string)

    def _handeln_template(self, data: dict, name: str=None) -> dict:
        '''
        Handeln potential template(s).  
        Check if a template is specified,
        if so and template unknow: raise an error,
        else merge template and given data.  
        Argument: `name` is for error tracking.
        '''
        if not 'template' in data.keys() and not 'templates' in data.keys():
            return data

        if 'template' in data.keys():
            tpl_names = [data.pop('template')]
        else:
            tpl_names = data.pop('templates')

        template = {}

        for tpl_name in tpl_names:
            
            assert tpl_name in self._templates.keys(), self._get_error('template', tpl_name, name)

            # merge tamplates
            template = {**template, **self._templates[tpl_name]}

        # finally add data
        return {**template, **data}

    def _process_special_attributes(self, data: dict) -> dict:
        '''
        For specific attribute extra processing is needed,  
        it is executed here.  
        Return the processed data
        '''
        if 'font' in data.keys():
            data['font'] = Font.f(data['font'])

        if 'color' in data.keys():
            data['color'] = self._get_color(data['color'])
        
        if 'text_color' in data.keys():
            data['text_color'] = self._get_color(data['text_color'])

        return data

    def _handeln_variables(self, data: dict):
        '''
        Look for variables (`"vars"` entry),  
        process & store variables  
        '''
        if not 'vars' in data.keys():
            return
        
        vars = data.pop('vars')

        self._process_expressions(vars, name='vars')
        self._add_new_vars(vars)

    def _handeln_imports(self, data: dict):
        '''
        Look for imports (`"imports"` entry),  
        process & store imports  
        '''
        if not 'imports' in data.keys():
            return
        
        imports: list = data.pop('imports')
        vars_imports = {}

        for name in imports:
            try:
                module = importlib.import_module(name)
                vars_imports[name] = module
            except ModuleNotFoundError:
                raise ModuleNotFoundError(self._get_error('module', name, key='imports'))
        
        self._add_new_vars(vars_imports)

    def _process_expressions(self, data: dict, name: str=None):
        '''
        Look for values with `$` and process them.  
        Update value of data with processed values.  
        '''
        for key in data.keys():
            
            if type(data[key]) != str:
                continue

            if data[key][0] == '$':
                data[key] = self._process_exp(data[key][1:], name=name, key=key)

    def _process_exp(self, exp: str, name: str=None, key: str=None):
        '''
        Process the value of an expression containing at least one variable  
        Args: name and key are for errors tracking.  
        Return the processed value
        '''
        original_exp = exp[:]
        
        # process lists
        lists = re.findall('(\[[^\]]+\])', exp)

        for _list in lists:
            exp = exp.replace(_list, f'np.array({_list})')

        # try to eval the expression
        try:
            exp = eval(exp, {'np':np}, self._vars)
        except:
            raise ValueError(self._get_error('exp', original_exp, name, key))

        return exp
    
    def _add_new_vars(self, data: dict):
        '''
        Set new variables.
        '''
        for name, value in data.items():

            # cast iterable to np.ndarray
            if type(value) in [list, tuple]:
                value = np.array(value)
            
            self._vars[name] = value

    def _get_error(self, category, value, name=None, key=None):
        '''
        Return a formatted error message.
        Parameters:  
        category: the type of error: ("var", "exp", "template")  
        value: the value specified in the error message  
        name: the key of the current entry (global)  
        key the key of the current entry (local)
        '''
        msg = ''

        if name != None:
            msg += f"\n\tName: '{name}' "
        
        if key != None:
            msg += f"\n\tKey: '{key}' "

        if category == 'var':
            msg += f"\n\tUnknown variable: '{value}'"
        
        elif category == 'exp':
            msg += f"\n\tCouldn't evaluate expression: {value}"
        
        elif category == 'template':
            msg += f"\n\tUnknown template: '{value}'"

        elif category == 'attribute':
            msg += f"\n\tInitialisation failed: '{value}'"

        elif category == 'module':
            msg += f"\n\tModule not found: '{value}'"

        return msg