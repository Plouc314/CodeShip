from .page import Page

class Application:
    '''
    Application object, manage the Page objects of the user interface.  

    Arguments:
    - pages: list (name, Page)
        List of all the pages of the application.
    '''


    def __init__(self, pages):
        
        self._active_page = pages[0][0]
        self._pages_history = []

        self._pages = {}
    
        for name, page in pages:
            self.add_page(name, page)

    def add_page(self, name, page):
        '''
        Add a page to the application.  

        Arguments:
        - name: the name of the page  
        - page: the instance of Page
        '''

        self._pages[name] = page
    
    def change_page(self, name):
        '''
        Change the active page.
        '''
        self._check_valid_name(name)

        # update the pages history
        # check if we go back of one page
        if len(self._pages_history) < 2:
            self._pages_history.append(name)

        elif self._pages_history[-2] == name:
            self._pages_history.pop(-1)
        
        else:
            self._pages_history.append(name)

        self._active_page = name

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

    def get_page(self, name):
        '''
        Return the page with the given name.
        '''
        self._check_valid_name(name)

        return self._pages[name]

    def react_events(self, pressed, events):
        '''
        React to the user input of the current frame.
        '''
        self._look_for_call()

        self._pages[self._active_page].react_events(pressed, events)

    def display(self):
        '''
        Display the current page.
        '''
        self._pages[self._active_page].display()

    def _look_for_call(self):
        '''
        Check if the active page has set a call.  
        If it is the case, change of page.
        '''
        if self._active_page._call == None:
            return
        
        if self._active_page._call == 'back':
            # go back of one page
            self.go_back()
        
        else:
            name = self._active_page._call

            self._check_valid_name(name)
            
            # go to the specified page
            self.change_page(name)

    def _check_valid_name(self, name):
        ''' 
        Return if name in pages, if not raise error.  
        '''
        if name in self._pages.keys():
            return True
        else:
            KeyError(f"There is no page named: '{name}'")