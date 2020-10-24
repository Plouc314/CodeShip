import pygame
from .form import Form
from .helper import Delayer, center_text, get_pressed_key, rl, get_dark_color, get_light_color
from .aux import Font, C
from .spec import Specifications as Spec

class Cadre(Form):
    '''
    Cadre object, like an Form with marges with the exception that it can be transparent.
    '''

    def __init__(self, dim, pos, color=C.WHITE, *, set_transparent=False, scale_dim=True, scale_pos=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, marge=True)
        
        self._is_transparent = set_transparent
        
        if set_transparent:
            self._surf['main'].set_colorkey(color)

    def _rescale_surf(self):
        # overwrite rescale method to keep the cadre transparent when rescaling
        super()._rescale_surf()
        
        if self._is_transparent:
            self._surf['main'].set_colorkey(self.color)

    def display(self, surface=None):
        super().display(marge=True, surface=surface)

class Button(Form):
    ''' 
    It's a button, can display text, has marge, can be pushed.

    Inherited from Form.

    Arguments:
        - text_color : color of the text
        - centered : if the text is centered
        - highlight : if the surface is highlighted when the mouse pass on it
        - surface : can set a custom surface, can be an image, numpy.ndarray, pygame.Surface
        - surf_font_color : if a custom surface is set & is partly transparent, surf_font color will fill the blanks
        - text : the text that is present at the beginning
    
    Methods:
        - pushed : Return if the surface has been clicked
        - display
    '''
    def __init__(self, dim, pos, color=C.WHITE, text='', *, text_color=C.BLACK, centered=True, font=Font.f(50), 
                    surface=None, with_font=False, scale_dim=True, scale_pos=True, highlight=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, surface=surface, with_font=with_font, marge=True)

        self._text = text
        
        self.text_color = text_color
        self.set_corners()
        self.highlighted = highlight
        self.centered = centered
        self.font = font

    def pushed(self, events):
        '''Return True if the object was clicked'''
        if self.on_it():
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    return True

    def get_text(self):
        ''' Return the text '''
        return self._text

    def highlight(self):
        '''
        Set the highlight color on surf, if custom surf with font: set highlight on surf font
        '''
        if self.on_it():
            # check if custom surf & font or normal unicolor
            if self._surf['type'] == 'custom':
                if self._surf['font']: # check if has a font
                    self._surf['font'].fill(self._high_color)
                else:
                    self._surf['main'].fill(self._high_color)
            else:
                self._surf['main'].fill(self._high_color)
        else:
            # check if custom surf
            if self._surf['type'] == 'custom':
                if self._surf['font']: # check if has a font
                    self._surf['font'].fill(self.color)
                else:
                    self._surf['main'] = pygame.transform.scale(self._surf['original'], rl(self._sc_dim))
            else:
                self._surf['main'].fill(self.color)

    def display_text(self, text=None, surface=None):
        '''
        Display the text of the instance.  
        If text is specified, display it instead of attribute text.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen

        if text == None:
            text = self._text

        if text == '':
            return
        
        # get marges
        x_marge, y_marge = center_text(self._sc_dim, self.font['font'], text)
        
        if not self.centered:
            x_marge = self._rs_marge_text
        
        # create font
        font_text = self.font['font'].render(text, True, self.text_color)
        
        # display font
        pos = rl(self._sc_pos[0] + x_marge, self._sc_pos[1] + y_marge)

        surface.blit(font_text, pos)

    def display(self, text=None, surface=None):
        '''
        Display the main surface, the marges and the text.  
        If a text is specified, display it instead of attribute text.  
        If a surface is specified, display on it, else display on the screen.
        '''
        # if highlight actived, handeln highlight color changes
        if self.highlighted:
            self.highlight()
        
        # display the surf
        super().display(marge=True, surface=surface)
        
        self.display_text(text=text, surface=surface)

class TextBox(Form):
    ''' 
    Display text, can have multiple lines and marges.

    Inherited from Form.

    Arguments:
        - text_color : color of the text
        - centered : if the text is centered
        - text : the text that is present at the beginning
        - marge : if it has marge or not
    
    Methods:
        - set_text : pass a string, can be on multiple lines
        - display
    '''
    def __init__(self, dim, pos, color=C.WHITE, text='', *,
                    text_color=C.BLACK, centered=True, font=Font.f(50), marge=False, scale_dim=True, scale_pos=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos)
        
        self._text = text
        self.centered = centered
        self.font = font
        self.lines = text.split('\n')
        self.text_color = text_color
        self.set_corners()
        self.as_marge = marge
       
        if marge:
            self._set_high_color()
            self.marge_color = self._high_color

    def get_text(self):
        ''' Return the text '''
        return self._text

    def set_text(self, text):
        ''' Set the text of the TextBox'''
        self._text = text
        self.lines = text.split('\n')

    def display_lines_text(self, surface=None):
        '''
        Display the text, can be on multiple lines.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen

        # split the box in n part for n lines
        y_line = round(self._sc_dim[1]/len(self.lines))
        
        for i, line in enumerate(self.lines):
            x_marge, y_marge = center_text((self._sc_dim[0],y_line), self.font['font'], line)
        
            if not self.centered:
                x_marge = self._rs_marge_text
        
            font_text = self.font['font'].render(line,True,self.text_color)
        
            surface.blit(font_text,rl(self._sc_pos[0]+x_marge,self._sc_pos[1]+i*y_line+y_marge))

    def display(self, surface=None):
        '''
        Display the TextBox  
        If a surface is specified, display on it, else display on the screen.
        '''
        super().display(marge=self.as_marge, surface=surface)

        self.display_lines_text(surface=surface)
        

get_input_deco = Delayer(Spec.TEXT_DELAY)
cursor_deco = Delayer(Spec.CURSOR_DELAY)

class InputText(Button):
    '''
    Get text input when triggered (clicked). Input text is stored in .content attribute

    Inherited from Button.

    Arguments:
    - text_color : color of the text
    - centered : if the text is centered
    - limit : the limit of character that can be entered
    - cache : if the input is hidden (with $ )
    - text : the text that is present at the beginning
    - pretext : text that disapear when the surface is clicked
    
    Methods:
    - pushed : Return if the surface has been clicked
    - run : Get input ( execute once by frame )
    - display
    '''
    CURSOR_WIDTH = 2
    is_cursor_displayed = True
    
    def __init__(self, dim, pos, color=C.WHITE, text='', *, text_color=C.BLACK, centered=False, font=Font.f(30),
                    limit=None, cache=False, scale_dim=True, scale_pos=True, pretext=None):

        super().__init__(dim, pos, color, text_color=text_color, centered=centered, font=font, scale_dim=scale_dim, scale_pos=scale_pos)
        
        self.active = False
        self.highlighted = True
        self.cursor_place = len(text)
        self.limit = limit # max char
        self.cache = cache # if true text -> $$$
        
        self.is_pretext = False
        self.pretext = pretext # if something: add a text that disapear when active

        self.set_text(text, with_pretext=self.pretext)

    def set_text(self, text, with_pretext=False):
        '''
        Set the text.  
        If `with_pretext=True`, set the pretext.
        '''
        self._text = str(text)
        self.cursor_place = len(self._text)

        self.is_pretext = with_pretext

    def reset_text(self):
        '''
        Reset the text, if has a pretext: set it.
        '''
        self._text = ''
        self.cursor_place = 0

        self.is_pretext = True

    @get_input_deco
    def is_moving_left(self, pressed):
        if pressed[pygame.K_LEFT]:
            return True

    @get_input_deco
    def is_moving_right(self, pressed):
        if pressed[pygame.K_RIGHT]:
            return True

    def check_text_length(self):
        '''
        If a limit is specified, check that the text is not longer that the limit.  
        Check that the text fit in the instance dimension.  
        If it is, remove the last char.
        '''
        # check for limit
        if self.limit != None:
            if len(self._text) > self.limit:
                self._text = self._text[:-1]
                self.cursor_place -= 1
                return

        # check that the text fit in dim
        try:
            center_text(self._sc_dim, self.font['font'], self._text,  ignore_exception=False)
        except ValueError:
            self._text = self._text[:-1]
            self.cursor_place -= 1

    def is_still_active(self, pressed, events):
        '''
        Return if the instance is still active.
        '''
        # check if RETURN is pressed
        if pressed[pygame.K_RETURN]:
            self.active = False
            return False
        
        # check if a click outside the instance's surface is made
        elif not self.on_it():
            pushed = False
            
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    pushed =  True 
            
            if pushed:
                self.active = False
                return False
        
        return True

    def manage_new_char(self, pressed):
        '''
        If a character has been pressed, add it to the text at the correct location.  
        Return True if a character has been added.
        '''
        key = get_pressed_key(pressed)
        
        if key == None:
            return False
        
        else:
            self._text = self._text[:self.cursor_place] + key + self._text[self.cursor_place:]
            self.cursor_place += 1
            
            self.check_text_length()
                
            return True

    def manage_char_deletion(self, pressed):
        '''
        If the backspace key has been pressed, update the text at the correct location.  
        Return True if a character has been deleted.
        '''
        if pressed[pygame.K_BACKSPACE]:
            self._text = self._text[:self.cursor_place-1] + self._text[self.cursor_place:]
            self.cursor_place -= 1
            return True

    def manage_cursor_change(self, pressed):
        '''
        Manage the changes of positions of the cursor.  
        Return True if the cursor moved.
        '''
        if self.is_moving_left(pressed):
            
            if self.cursor_place > 0:
                self.cursor_place -= 1
                return True
        
        if self.is_moving_right(pressed):
            
            if self.cursor_place < len(self._text):
                self.cursor_place += 1
                return True

    @get_input_deco
    def get_input(self, events, pressed):
        '''
        Manage the input of the instance.  
        Check for end of `self.active`.
        Get character input, manage cursor position.  
        '''
        
        if not self.is_still_active(pressed, events):
            return False

        # check for new char
        if self.manage_new_char(pressed):
            return True
        
        # check for char deletion
        if self.manage_char_deletion(pressed):
            return True
    
        # check for cursor change
        if self.manage_cursor_change(pressed):
            return True

        return False
    
    def display_text_cursor(self, surface=None):
        '''
        Display the cursor at the correct location.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen


        # get text dim until cursor position
        width, height = self.font['font'].size(self._text[:self.cursor_place])
        
        # get marges
        x_marge, y_marge = center_text(self._sc_dim, self.font['font'], self._text[:self.cursor_place])
        if not self.centered:
            x_marge = self._rs_marge_text

        # get cursor pos
        x = self.TOPLEFT[0] + width + x_marge
        y_top = self.TOPLEFT[1] + y_marge
        y_bottom = self.BOTTOMLEFT[1] - y_marge

        top_pos = rl(x, y_top)
        bottom_pos = rl(x, y_bottom)
        
        if self.is_cursor_displayed:
            pygame.draw.line(surface, C.BLACK, top_pos, bottom_pos, self.CURSOR_WIDTH)
    
        self.change_cursor_state()

    @cursor_deco
    def change_cursor_state(self):
        ''' Make the cursor blink '''
        self.is_cursor_displayed = not self.is_cursor_displayed
        return True

    def run(self, events, pressed):
        
        if self.pushed(events):
            self.active = True
            # if pretext, remove pretext
            self.is_pretext = False
        
        if self.active:
            self.get_input(events, pressed)

    def display(self, surface=None):
        '''
        Display the InputText  
        If a surface is specified, display on it, else display on the screen.
        '''

        # set string to be displayed
        if self.is_pretext:
            string = self.pretext

        elif self.cache:
            string = '$' * len(self._text)

        else:
            string = self._text

        super().display(text=string, surface=surface)
        
        if self.active:
            self.display_text_cursor(surface=surface)


class ScrollList(Form):

    WIDTH_SCROLL_BAR = Spec.WIDTH_SCROLL_BAR

    def __init__(self, dim, pos, elements, *, color=C.WHITE, 
                    scale_dim=True, scale_pos=True, bar_color=C.LIGHT_GREY):
        
        super().__init__(dim, pos, color=color, marge=True,
                scale_pos=scale_pos, scale_dim=scale_dim)
        
        self._elements = list(elements)
        self._bar_color = bar_color

        self._selected = False

        # y dimension of all elements (unscaled)
        self._tot_y = sum((element._unsc_dim[1] for element in self._elements))

        # the position of the cursor in % -> between 0 and ?
        self._cursor_y_per = 0

        # the y limits of the surface to be displayed
        self._top_lim = 0
        self._bottom_lim = self._unsc_dim[1]

        self._set_scroll_bar()

    def add_element(self, element, index=None):
        '''
        Add an element to the scroll list.
        if an index is specified, add the element at the given index.
        '''
        if index == None:
            index = len(self._elements)
        
        self._elements.insert(index, element)

        # update tot_y, scroll bat
        self._tot_y += element._unsc_pos[1]

        self._set_scroll_bar()

    def run(self, events, pressed):
        '''
        React to the user input, update the scroll cursor, the displayed part of the list.
        '''
        # update selected attr
        if not self._selected:
            
            if self._is_selected(events):
                self._selected = True

                # higlight scroll cursor
                self._scroll_cursor.set_color(get_light_color(self._bar_color))
        else:
            if self._is_still_selected(events):
                self._selected = True
            else:
                self._selected = False
                self._scroll_cursor.set_color(self._bar_color)

        if self._selected:
            self._update_scroll_bar_pos()
            
    def _update_scroll_bar_pos(self):
        '''
        When scroll bar is selected, 
        update its position according to the mouse position.  
        Update the limits of the displayed elements.
        '''
        mouse_y = pygame.mouse.get_pos()[1]
        mouse_y = self._y_in_boundaries(mouse_y)

        # update postion
        new_pos = [
            self._scroll_cursor.get_center(scale=True)[0],
            mouse_y
        ]

        self._scroll_cursor.set_pos(new_pos, center=True)

        # update scroll cursor state
        rel_y = mouse_y - self._sc_pos[1]

        # handeln the marge
        rel_y -= self._scroll_cursor._sc_dim[1]//2

        self._cursor_y_per = rel_y / self._sc_dim[1]

        # update limits
        self._top_lim = (self._tot_y * self._cursor_y_per)
        self._bottom_lim = (self._tot_y * self._cursor_y_per) + self._unsc_dim[1]

    def _y_in_boundaries(self, y):
        '''
        Check if given position (scaled) is in the scroll bar boundaries,
        Return the in boundaries position.
        '''
        top_lim = self._sc_pos[1] + self._scroll_cursor._sc_dim[1]//2
        bottom_lim = self._sc_pos[1] + self._sc_dim[1] - self._scroll_cursor._sc_dim[1]//2

        if y < top_lim:
            return top_lim
        
        if y > bottom_lim:
            return bottom_lim
        
        return y

    def _get_displayed_elements(self):
        '''
        Select the elements to be displayed,
        set their relative position.  
        Return a list of the selected elements.
        '''
        elements = []
        y = 0

        for element in self._elements:

            y_top = y
            y_bottom = y + element._unsc_dim[1]

            # check if element is displayed
            if y_bottom > self._top_lim and y_top < self._bottom_lim:
                
                rel_pos = [0, y - self._top_lim]
                element.set_pos(rel_pos, scale=True)
                
                elements.append(element)

            y += element._unsc_dim[1]
        
        return elements

    def _is_selected(self, events):
        '''
        Return if the scroll cursor is selected.  
        Selected means mouse button down and mouse cursor on scroll cursor.
        '''
        if self.on_it():
            is_pressed = pygame.mouse.get_pressed()[0]
            return is_pressed

    def _is_still_selected(self, events):
        '''
        Return if the scroll cursor is still selected, meaning if the mouse button is still down.
        '''
        return pygame.mouse.get_pressed()[0]

    def _set_scroll_bar(self):
        '''
        Set the scroll bar: the bar rectangle and the moving cursor.
        '''
        # rectangle bar
        dim = (self.WIDTH_SCROLL_BAR, self._unsc_dim[1])
        pos = (
            self._unsc_pos[0] + self._unsc_dim[0] - self.WIDTH_SCROLL_BAR,
            self._unsc_pos[1]
        )
        rect_color = get_dark_color(self._bar_color)

        self._rect_bar = Form(dim, pos, color=rect_color, marge=True)

        # scroll cursor
        dim_y = self._unsc_dim[1] * (self._unsc_dim[1] / self._tot_y)
        dim = (self.WIDTH_SCROLL_BAR, dim_y)

        dif_y = self._cursor_y_per * self._unsc_dim[1]
        pos = (
            self._unsc_pos[0] + self._unsc_dim[0] - self.WIDTH_SCROLL_BAR, 
            self._unsc_pos[1] + dif_y
        )

        self._scroll_cursor = Form(dim, pos, color=self._bar_color)

    def display(self):
        '''
        Display the scroll list.
        '''
        # reset surface
        self.set_surface()

        elements = self._get_displayed_elements()
        
        for element in elements:
            element.display(surface=self.get_surface('main'))


        super().display(marge=True)

        self._rect_bar.display()
        self._scroll_cursor.display()
