from .page import Page
from .interface import Interface

class Application:
    '''
    Application object  
    Manage the `Page` objects attached to it.

    Parameters
    ---
    `pages`: list[tuple[str, Page]]  
    List of tuple containing each time, the name and the page and the `Page` object.
    
    Methods
    ---
    `add_page`: Add a page to the application.  
    `get_page`: Return the specified page.  
    `change_page`: Change the active page.  
    `go_back`: Change the active page to be the previous one.  
    `add_frame_function`: Add a function that will be executed at each frame.  
    `set_frame_function_state`: Set if the function is executed or not.  
    `set_in_page_func`: Set a function that will be executed when getting in a page.  
    `set_out_page_func`: Set a function that will be executed when getting out a page.  
    `react_events`: React to the user inputs, execute `react_events` function of active page.  
    `display`: Display the active page.  
    '''

    def __init__(self, pages):
        
        self._active_page = pages[0][0]
        self._pages_history = [self._active_page]

        self._pages = {}

        for name, page in pages:
            self.add_page(name, page)
        
        self._frame_funcs = []
        self._pages_frame_funcs = {page:[] for page in self._pages.keys()}
        self._active_frame_funcs = []

        # functions called when the page change to a new one
        self._in_pages = {page: None for page in self._pages}
        self._out_pages = {page: None for page in self._pages}

    def add_page(self, name, page):
        '''
        Add a page to the application.  

        Arguments:
        - name: the name of the page  
        - page: the instance of Page
        '''

        self._pages[name] = page
    
    def change_page(self, name, state=None):
        '''
        Change the active page.  
        If state is specified, set the state of the new page.
        '''
        self._check_valid_page(name)

        # look for out_page function
        if self._out_pages[self._active_page] != None:
            self._out_pages[self._active_page]()

        # update the pages history
        # check if we go back of one page
        if len(self._pages_history) < 2:
            self._pages_history.append(name)

        elif self._pages_history[-2] == name:
            self._pages_history.pop(-1)
        
        else:
            self._pages_history.append(name)

        self._active_page = name

        if state == None:
            # exec page on_change_page function
            self._pages[name]._on_change_page()

        else:
            self._pages[name].change_state(state)

        # look for in_page function
        if self._in_pages[name] != None:
            self._in_pages[name]()
        
        # for static interface, set frame to be displayed
        Interface.set_frame_to_display()

    def go_back(self):
        '''
        Change the active page to be the one before the current.  
        So if we pass from `page1` to `page2` and call `go_back`, we will be at `page1`.
        '''
        # check if can go back
        if len(self._pages_history) < 2:
            raise BaseException("Can't go back: current page is root page.")

        new_page = self._pages_history[-2]

        # update pages histoty
        self._pages_history.pop(-1)

        self.change_page(new_page)

    def get_active_page(self) -> Page:
        '''
        Return the active page.
        '''
        return self._pages[self._active_page]

    def get_page(self, name) -> Page:
        '''
        Return the page with the given name.
        '''
        self._check_valid_page(name)

        return self._pages[name]

    def add_frame_function(self, func, active_pages=None, is_active=False):
        '''
        Add a function that will be executed every frame.  

        Arguments:
        - is_active: if the function will be executed at each frame, to change the function state (if it's executed) call the set_frame_function_state method.
        - active_pages: if specified, the page(s) where the frame function will be executed.
        '''
        self._frame_funcs.append(func)
        
        if not active_pages is None:

            if type(active_pages) != list:
                active_pages = [active_pages]

            for page in active_pages:
                self._pages_frame_funcs[page].append(func)

        if is_active:
            self._active_frame_funcs.append(func)

    def set_frame_function_state(self, func, state: bool):
        '''
        Change the state of the given function, if it's executed or not.
        '''
        if state:
            # check if function has been set previously
            try:
                idx = self._frame_funcs.index(func)
            except ValueError:
                raise ValueError(f"Function {func.__name__} isn't part of the app's frame functions.")
            
            # set function in active frame functions
            if not func in self._active_frame_funcs:
                self._active_frame_funcs.append(func)

        else:
            # check if function is an active function
            try:
                idx = self._active_frame_funcs.index(func)
            except ValueError:
                return
            
            self._active_frame_funcs.remove(func)

    def set_in_page_func(self, page, func):
        '''
        Set a function that will be executed when getting in the specified page.
        '''
        self._check_valid_page(page)

        self._in_pages[page] = func

    def set_out_page_func(self, page, func):
        '''
        Set a function that will be executed when getting out of the specified page.
        '''
        self._check_valid_page(page)

        self._out_pages[page] = func

    def react_events(self, pressed, events):
        '''
        React to the user input of the current frame.
        '''
        self._look_for_call()

        for func in self._active_frame_funcs:
            self._safe_exec_func(func)

        for func in self._pages_frame_funcs[self._active_page]:
            self._safe_exec_func(func)

        self._pages[self._active_page].react_events(pressed, events)

    def display(self):
        '''
        Display the current page.
        '''
        # in case of static interface, check if the surface need to be displayed
        if Interface.is_static() and not Interface.is_frame_displayed():
            return

        self._pages[self._active_page].display()

    def _look_for_call(self):
        '''
        Check if the active page has set a call.  
        If it is the case, change of page.
        '''
        page = self._pages[self._active_page]


        if page._call == None:
            return
        
        if page._call == 'back':
            # go back of one page
            self.go_back()
        
        else:
            name = page._call

            self._check_valid_page(name)
            
            # go to the specified page
            self.change_page(name)
        
        # reset call
        page._call = None

    def _check_valid_page(self, name):
        ''' 
        Return if name in pages, if not raise error.  
        '''
        if name in self._pages.keys():
            return True
        else:
            KeyError(f"There is no page named: '{name}'")
    
    def _safe_exec_func(self, func):
        '''
        Try the given function.
        '''
        try:
            func()
        except:
            raise RuntimeError(f"There was an error in given function: {func.__name__}")