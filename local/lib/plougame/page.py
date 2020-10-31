from .aux import Dimension
from .components import Button, InputText, ScrollList

class Page:
    '''
    Page object, manage the components (Form like objects) of a page.  

    Arguments:
    - states: All the possible states of the page
    - components: list, (name, object)
        Take all the components of the page.
    - active_states: take either 'none' or 'all', the default active states of the components
    
    Methods:
    - add_component: Add a component to the page
    - get_component: Get the specified component
    - set_states_components: Set the states of one or more components
    - change_state: Change the active state of the page
    - go_back: Change the state to be the previous one
    - add_button_logic: Add a function to be executed when button is pushed
    - react_events, display
    - get_text: Get the text of an InputText component
    - set_text: Set the text of a component
    - set_in_state_func: Set a function to be executed when entering the state
    - set_out_state_func: Set a function to be executed when getting out of the state
    - change_page: Set a call for an Application object to change the current page
    - change_display_state: Set if a component is displayed, independently of the active state
    '''

    def __init__(self, states, components, active_states='none'):
        
        self._states = list(states)
        self._states_history = [states[0]]
        self._active_state = states[0]

        # functions called when the state change to a new one
        self._in_states = {state: None for state in self._states}
        self._out_states = {state: None for state in self._states}

        # To use with App,
        # call is a message addressed to the App, to change of page (for now)
        self._call = None

        self._components = {}
        self._subpages = {}
        self._buttons = {}
        self._inputs = {}
        self._scrolls = {}

        if active_states == 'none':
            active_states = []
        elif active_states == 'all':
            active_states = None
        else:
            raise ValueError(f"Invalid value for active_states: {active_states}")

        for name, obj in components:
            self.add_component(name, obj, active_states=active_states)
    
    def change_page(self, new_page):
        '''
        Need to be member of an Application object.

        Set a call for the Application object to change the active page.
        '''
        self._call = new_page

    def change_state(self, new_state):
        '''
        Change the active state of the page.  
        Reset the text of all InputText objects of old state.  
        Execute the potential "in state" or "out state" function.
        '''
        self._check_valid_state(new_state)

        # reset inputs of old state
        self._reset_inputs_text(self._active_state)

        # look for out_state function
        if self._out_states[self._active_state] != None:
            self._out_states[self._active_state]()

        # update the states history
        # check if we go back of one state
        if self._states_history[-1] == new_state:
            pass

        elif len(self._states_history) < 2:
            self._states_history.append(new_state)

        elif self._states_history[-2] == new_state:
            self._states_history.pop(-1)
        
        else:
            self._states_history.append(new_state)

        self._active_state = new_state

        # look for in_state function
        if self._in_states[new_state] != None:
            self._in_states[new_state]()

    def set_in_state_func(self, state, func):
        '''
        Set a function that will be executed when getting in the specified state.
        '''
        self._check_valid_state(state)

        self._in_states[state] = func

    def set_out_state_func(self, state, func):
        '''
        Set a function that will be executed when getting out of the specified state.
        '''
        self._check_valid_state(state)

        self._out_states[state] = func

    def get_state(self):
        ''' Return the active state. '''
        return self._active_state

    def go_back(self):
        '''
        Change the active state to be the one before the current.  
        So if we pass from `state1` to `state2` and call `go_back`, we will be at `state1`.
        '''
        
        # check if can go back
        if len(self._states_history) < 2:
            # set a call -> go back of one page
            self._call = "back"
            return
        
        new_state = self._states_history[-2]

        # update states histoty
        self._states_history.pop(-1)

        self.change_state(new_state)

    def get_component(self, name):
        '''
        Return the component with the specified name.
        '''
        self._check_valid_name(name)

        return self._components[name]['object']

    def add_component(self, name, obj, active_states=None):
        '''
        Add a component to the page.  
        The component can be a subclass of one of these: SubPage, Form, Cadre, TextBox, Button, InputText

        Arguments:
        - name: the name of the component  
        - obj: the instance of the component
        - active_states: the states where the component will be active, by default: all
        '''

        if active_states == None:
            active_states = self._states.copy()
        else:
            active_states = active_states.copy()

        # add attribute to the component
        comp_info = {
            'object': obj,
            'active states': active_states,
            'displayed': False
        }
        
        self._components[name] = comp_info

        # look if component is a subpage
        if isinstance(comp_info['object'], SubPage):
            self._subpages[name] = comp_info

        # look if object that react to events
        elif type(comp_info['object']) == Button:
            
            # add butto func attr
            comp_info['func'] = None
            self._buttons[name] = comp_info
        
        elif type(comp_info['object']) == InputText:
            self._inputs[name] = comp_info
        
        elif isinstance(comp_info['object'], ScrollList):
            self._scrolls[name] = comp_info

    def add_button_logic(self, name, func):
        '''
        Add a function to be executed when the specified button is pushed, 
        equivalent to `Button.set_logic`.

        Arguments:
        - name: the name of the button
        - func: the function to be executed
        '''

        self._check_valid_name(name, self._buttons)
        comp_info = self._buttons[name]

        # add func and active states to component info
        comp_info['func'] = func

    def set_states_components(self, states, names):
        '''
        Set the component(s) that are active for the given state(s).  

        Arguments:
        - states: str / list
            The state(s) that will be set as active on the specifed component(s).
            If given value is None, all states will be set.
        - names: str / list
            The name(s) of the component(s)
        '''
        
        # pass args to list
        if states == None:
            states = self._states
        elif type(states) == str:
            states = [states]
        
        if type(names) != list:
            names = [names]

        for name in names:
            self._check_valid_name(name)
            comp_info = self._components[name]

            # reset states
            comp_info['active states'] = []

            for state in states:
                self._check_valid_state(state)
                if not state in comp_info['active states']:
                    comp_info['active states'].append(state)

    def change_display_state(self, name, is_displayed):
        '''
        Set if the component will be displayed, independently of the active state.
        '''
        self._check_valid_name(name)

        comp_info = self._components[name]

        comp_info['displayed'] = is_displayed

    def get_text(self, name):
        '''
        Return the text of an InputText component.
        '''
        self._check_valid_name(name, self._inputs)

        return self._inputs[name]['object'].get_text()

    def set_text(self, name, text):
        '''
        Set the text of one of the component.
        '''
        self._check_valid_name(name)

        obj = self._components[name]['object']

        obj.set_text(text)

    def react_events(self, pressed, events):
        '''
        React to the user input of the current frame.  
        '''
        # run subpages
        for sub_info in self._get_active_comps(self._subpages):
            sub_info['object'].react_events(pressed, events)

        # run inputs
        for inp_info in self._get_active_comps(self._inputs):

            inp_info['object'].run(events, pressed)

        # run scroll lists
        for scroll_info in self._get_active_comps(self._scrolls):

            scroll_info['object'].run(events, pressed)

        # run buttons
        for butt_info in self._get_active_comps(self._buttons):

            if butt_info['object'].pushed(events) and butt_info['func'] != None:
                # execute button's when-pushed function
                butt_info['func']()

    def display(self):
        '''
        Display all components in the active state.  
        Display all components that were manualy set to be displayed.
        '''
        for comp_info in self._components.values():

            if self._active_state in comp_info['active states'] or comp_info['displayed']:
                comp_info['object'].display()

    def _on_change_page(self):
        '''
        Executed when this page become the active page.
        '''
        # call change_state -> reset_inputs, exec in_state func
        self.change_state(self._active_state)

    def _reset_inputs_text(self, state):
        '''
        Reset the texts of the InputText objects of the given state.
        '''
        for inp_info in self._get_active_comps(self._inputs, state=state):
            inp_info['object'].reset_text()

    def _get_active_comps(self, _dict=None, state=None):
        '''
        Generator, yield component dicts of the active state.  
        By default, the _dict is `self._components`.  
        If state is specified, use given state instead of active state.
        '''
        if _dict == None:
            _dict = self._components

        if state == None:
            state = self._active_state

        for comp_info in _dict.values():
            if state in comp_info['active states']:
                yield comp_info

    def _check_valid_name(self, name, _dict=None):
        ''' 
        Return if name in components, if not raise error.  
        If dict is specified, look for name in specified dict.
        '''
        if _dict == None:
            _dict = self._components

        if name in _dict.keys():
            return True
        else:
            KeyError(f"There is no component named: '{name}'")

    def _check_valid_state(self, state):
        ''' Return if the state is in states, if not raise error. '''
        if state in self._states:
            return True
        else:
            raise ValueError(f"There is no state named: '{state}'.")


class SubPage(Page):

    def __init__(self, states, components, pos, active_states='none'):

        super().__init__(states, components, active_states=active_states)

        self.set_pos(pos)
        
    def set_pos(self, pos, is_scaled=False):
        '''
        Set the position of the SubPage.  

        Arguments:
        - pos: the position
        - is_scaled: if the given position is scaled
        '''

        if is_scaled:
            self._sc_pos = list(pos)
            self._unsc_pos = Dimension.inv_scale(pos)
        
        else:
            self._unsc_pos = list(pos)
            self._sc_pos = Dimension.scale(pos)
    
        self._set_dif_pos()

    def _set_dif_pos(self):
        '''
        Set the difference of position of all the components for the `on_it` method,
        set the `_dif_pos_on_it` attribute of `Form`.
        '''
        for comp_info in self._components.values():
            comp_info['object']._dif_pos_on_it = self._unsc_pos

    def display(self, dif_pos=None):
        '''
        Display all components in the active state.  
        Display all components that were manualy set to be displayed.  
        Take the position into account to display everything.  
        if dif_pos is specified, the origin position will be `position + dif_pos`
        '''

        for comp_info in self._components.values():

            if self._active_state in comp_info['active states'] or comp_info['displayed']:
            
                if isinstance(comp_info['object'], SubPage):
                    comp_info['object'].display(dif_pos=self._sc_pos)

                else:
                    pos = (
                        self._sc_pos[0] + comp_info['object'].get_pos(scaled=True)[0],
                        self._sc_pos[1] + comp_info['object'].get_pos(scaled=True)[1],
                    )
                    
                    comp_info['object'].display(pos=pos)
        