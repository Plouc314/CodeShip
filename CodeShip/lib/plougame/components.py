import pygame
import numpy as np
import functools
from .form import Form
from .helper import Delayer, center_text, get_pressed_key, get_dark_color, get_light_color
from .auxiliary import Dimension, Font, C
from .spec import Specifications as Spec
from typing import List, Dict, Tuple, Union

class Cadre(Form):
    '''
    Cadre object, like an Form with marges with the exception that it can be transparent.
    '''

    def __init__(self, dim, pos, color=C.WHITE, *, set_transparent=False, 
                scale_dim=True, scale_pos=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, marge=True)
        
        self._is_transparent = set_transparent
        
        if set_transparent:
            self._surf['main'].set_colorkey(color)

    def _rescale_surf(self):
        # overwrite rescale method to keep the cadre transparent when rescaling
        super()._rescale_surf()
        
        if self._is_transparent:
            self._surf['main'].set_colorkey(self._color)

    def display(self, surface=None, pos=None):
        super().display(marge=True, surface=surface, pos=pos)
    
    def __repr__(self):
        return "Cadre Object"

class Button(Form):
    ''' 
    Button, can display text, can be pushed.

    Inherited from Form.

    Parameters
    ---
    `text_color`: tuple  
    The color of the text
    
    `centered`: bool  
    If the text is centered

    `text`: str
    The text that is present at the beginning

    `font`: dict[int, pygame.font]  
    The font used to display the text, strongly recommended to use `Font.f()`
    (as in default value).

    `highlight`:  
    If the surface is highlighted (color changes slightly) when the mouse passes over it.

    `surface`:  
    can set a custom surface, can be an image, numpy.ndarray, pygame.Surface.

    `with_font`: bool  
    If True and a custom surface is specified, potential empty pixels in the surface
    will be filled with the given `color`.

    `has_marge`: bool  
    If it has marge or not.

    Methods
    ---
    `set_text`: Set the text displayed  
    `get_text`: Return text attribute  
    `set_font`: Set the font used to display the text  
    `get_font`: Return the font used to display the text  
    `pushed`: Return if the instance has been clicked.  
    `set_logic`: Define the function executed when the button is pushed
    (must execute `run` method).  
    `run`: Execute logic function (set with `set_logic`) when `pushed` return True,
    if logic is set must be executed each frame (done automatically when instance in `Page`).  
    `display`: Display the instance.  
    '''
    def __init__(self, dim, pos, color=C.WHITE, text='', *, text_color=C.BLACK,
                centered=True, font=Font.f(50), surface=None, with_font=False,
                scale_dim=True, scale_pos=True, highlight=True, has_marge=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, 
                        surface=surface, with_font=with_font, marge=True)

        self._text = text
        self.text_color = text_color
        self._highlighted = highlight
        self._centered = centered
        self._has_marge = has_marge
        self._font = font
        self._logic = None

    def pushed(self, events):
        '''Return True if the object was clicked'''
        if self.on_it():
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    return True

    def set_text(self, text: str):
        ''' Set the text'''
        self._text = text

    def get_text(self) -> str:
        ''' Return the text '''
        return self._text

    def set_font(self, font:pygame.font.Font, size:int):
        '''
        Set the font of the instance.
        '''
        self._font = {'size':size, 'font':font}
    
    def get_font(self) -> dict:
        '''
        Return the instance's font on the format:
        {"size" `int`, "font" `pygame.font.Font`}
        '''
        return self._font.copy()

    def set_logic(self, func):
        '''
        Set the function which will be called when `pushed` returns True.
        '''
        self._logic = func

    def run(self, events, pressed):
        '''
        React to the user input, execute the given logic function if given.
        '''
        if not self._logic is None and self.pushed(events):
            self._logic()

    def _highlight(self):
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
                    self._surf['font'].fill(self._color)
                else:
                    self._surf['main'] = pygame.transform.scale(self._surf['original'], self._sc_dim.astype(int))
            else:
                self._surf['main'].fill(self._color)

    def display_text(self, text=None, surface=None, pos=None):
        '''
        Display the text of the instance.  
        If text is specified, display it instead of attribute text.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen

        if pos is None:
            pos = self._sc_pos

        if text == None:
            text = self._text

        if text == '':
            return
        
        # get marges
        x_marge, y_marge = center_text(self._sc_dim, self._font['font'], text)
        
        if not self._centered:
            x_marge = self._rs_marge_text
        
        # create font
        font_text = self._font['font'].render(text, True, self.text_color)
        
        # display font
        pos = np.array([pos[0] + x_marge, pos[1] + y_marge], dtype=int)

        surface.blit(font_text, pos)

    def display(self, text=None, surface=None, pos=None):
        '''
        Display the main surface, the marges and the text.  
        If a text is specified, display it instead of attribute text.  
        If a surface is specified, display on it, else display on the screen.
        '''
        # if highlight actived, handeln highlight color changes
        if self._highlighted:
            self._highlight()
        
        # display the surf
        super().display(marge=self._has_marge, surface=surface, pos=pos)
        
        self.display_text(text=text, surface=surface, pos=pos)

    def __repr__(self):
        return "Button Object"

class TextBox(Form):
    ''' 
    Display text, can have multiple lines and marges.

    Inherited from Form.

    Parameters
    ---
    `text_color`: tuple  
    The color of the text
    
    `centered`: bool  
    If the text is centered

    `text`: str/list  
    The text that is present at the beginning
    
    `font`: dict[int, pygame.font]  
    The font used to display the text, strongly recommended to use `Font.f()`
    (as in default value).

    `marge`: bool  
    If it has marge or not
    
    `dynamic_dim`: bool  
    If True, the dimention will be adjusted to the text
    
    `continuous_text`: bool  
    If True, the space (y dimension) between the lines will
    be the minimal one (unlike the default setting where each line is placed to
    occupy the entire space)

    Methods
    ---
    `set_text`: Set the text displayed, can be on multiple lines  
    `get_text`: Return text attribute  
    `set_font`: Set the font used to display the text  
    `get_font`: Return the font used to display the text  
    `set_text_color`: Set the color of the text  
    `set_marge_text`: Set the marge used with the text  
    `set_centered`: Set if the text is centered  
    `display`: Display the instance.  
    '''

    def __init__(self, dim, pos, color=C.WHITE, text='', *,
                    text_color=C.BLACK, centered=True, 
                    font=Font.f(50), marge=False, 
                    scale_dim=True, scale_pos=True, 
                    dynamic_dim=False, continuous_text=False):
        
        if dynamic_dim:
            # set a default dimension to doesn't produce any error in Form.__init__
            dim = (10,10)

        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, marge=marge)
        
        self._centered = centered
        self._font = font
        self._as_marge = marge
        self._is_dynamic = dynamic_dim
        self._continuous_text = continuous_text
        self._rendered_text = None

        self._text_color = text_color
        self._is_multiples_colors = False
        self._text_colors = []
        
        self.set_text(text)

        if self._is_dynamic:
            self._set_dim_as_to_text()

    def set_marge_text(self, width: int, scaled=False):
        '''
        Set the width of the marge used with the text.

        Parameters
        ---
        `width`: int  
        The width of the marge

        `scaled`: bool  
        If the given width is scaled to the current window dimension
        '''
        if scaled:
            self.MARGE_TEXT = Dimension.inv_scale(width)
            self._rs_marge_text = round(width)
        else:
            self.MARGE_TEXT = round(width)
            self._rs_marge_text = Dimension.E(width)

    def set_font(self, font:pygame.font.Font, size:int):
        '''
        Set the font of the instance.
        '''
        self._font = {'size':size, 'font':font}
    
    def get_font(self) -> dict:
        '''
        Return the instance's font on the format:
        {"size" `int`, "font" `pygame.font.Font`}
        '''
        return self._font.copy()

    def set_text_color(self, color: Union[list, tuple]):
        '''
        Set the text color,  
        the color argument can be either a color,
        in that case set the color of the whole text, 
        or a list of color (one per line), in that case
        each line will have its own color.
        '''
        if type(color) == list:
            # check that there is one color per line
            assert len(color) == len(self._lines), "Must give one color per line."

            self._is_multiples_colors = True
            self._text_colors = color
        
        else:
            self._is_multiples_colors = False
            self._text_color = color

    def get_text(self, lines: bool = False) -> Union[str, list]:
        '''
        Return the text of the TextBox,  
        If `lines=True`, return a list of the lines of the text,
        else return a string.
        '''
        if lines:
            return self._lines.copy()
        else:
            return self._text[:]

    def set_text(self, text: Union[str, list]):
        '''
        Set the text of the TextBox.  
        The `text` argument can be either str or list[str].
        '''
        if type(text) == list:
            self._text = functools.reduce(lambda x,y: x + '\n' + y, text)
            self._lines = list(text)
        else:
            self._text = text
            self._lines = text.split('\n')

        # set rendered text cache : TODO
        self._rendered_text = []
        for line in self._lines:
            self._rendered_text.append( None )

        if self._is_dynamic:
            self._set_dim_as_to_text()

    def set_centered(self, value: bool):
        '''
        Set if the text is centered,  
        (same as `centered` argument in `__init__` method).
        '''
        self._centered = value

    def _set_dim_as_to_text(self):
        '''
        Set the dim of the instance according to the text.
        '''
        biggest_line = ' ' + max(self._lines, key=len) + ' '
        width, height = self._font['font'].size(biggest_line)

        dim = [
            width + self._rs_marge_text,
            len(self._lines) * (height + self._rs_marge_text // 2)
        ]

        # add a bit more marges
        dim[1] += self._rs_marge_text

        self.set_dim(dim)

    def _display_lines_text(self, surface=None, pos=None):
        '''
        Display the text, can be on multiple lines.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen

        if pos is None:
            pos = self._sc_pos

        # set color
        if not self._is_multiples_colors:
            colors = [self._text_color for _ in range(len(self._lines))]
        else:
            colors = self._text_colors

        if not self._continuous_text:
            # split the box in n part for n lines
            y_line = round(self._sc_dim[1]/len(self._lines))
        else:
            width, height = self._font['font'].size(self._lines[0])
            y_line = height + self._rs_marge_text

        for i, line in enumerate(self._lines):
            x_marge, y_marge = center_text((self._sc_dim[0], y_line), self._font['font'], line)
        
            if not self._centered:
                x_marge = self._rs_marge_text
        
            font_text = self._font['font'].render(line, True, colors[i])
        
            surface.blit(font_text, np.array([pos[0] + x_marge, pos[1] + i * y_line + y_marge], dtype=int))

    def display(self, surface=None, pos=None):
        '''
        Display the TextBox  
        If a surface is specified, display on it, else display on the screen.
        '''
        super().display(marge=self._as_marge, surface=surface, pos=pos)

        self._display_lines_text(surface=surface, pos=pos)

    def __repr__(self):
        return "TextBox Object"    

get_input_deco = Delayer(Spec.TEXT_DELAY)
cursor_deco = Delayer(Spec.CURSOR_DELAY)

class InputText(Button):
    '''
    Get text input when triggered (clicked). Input text is stored in .content attribute

    Inherited from Button.

    Parameters
    ---
    `text_color`: tuple  
    The color of the text.
    
    `centered`: bool  
    If the text is centered.

    `text`: str
    The text that is present at the beginning.

    `font`: dict[int, pygame.font]  
    The font used to display the text, strongly recommended to use `Font.f()`
    (as in default value).

    `limit`: int  
    The limit of character that can be entered.

    `cache`: bool  
    If True, the displayed text will be hidden (with `$`).

    `pretext`: str  
    Text that is present initialy and disapears when the surface is clicked.

    `has_marge`: bool  
    If it has marge or not.

    Methods
    ---
    `set_text`: Set the text, can set back the pretext.  
    `reset_text`: Clear the text, can set a new pretext.  
    `pushed`: Return if the instance has been clicked.  
    `run`: Manage instance, get inputs, must be executed each frame
    (done automatically when instance in `Page`).  
    `display`: Display the instance.
    '''
    COLOR_PRETEXT = C.GREY
    is_cursor_displayed = True
    
    def __init__(self, dim, pos, color=C.WHITE, text='', *, text_color=C.BLACK, 
                centered=False, font=Font.f(30), limit=None, cache=False, 
                scale_dim=True, scale_pos=True, pretext=None, has_marge=True):

        super().__init__(dim, pos, color, text_color=text_color, has_marge=has_marge,
                centered=centered, font=font, scale_dim=scale_dim, scale_pos=scale_pos)
        
        # set Specifications
        self.CURSOR_WIDTH = Spec.CURSOR_WIDTH

        self.active = False
        self._base_text_color = text_color
        self._highlighted = True
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

    def reset_text(self, pretext=None):
        '''
        Reset the text, if has a pretext: set it.  
        If `pretext` argument is specified, set a new pretext.
        '''
        if not pretext is None:
            self.pretext = pretext

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
            center_text(self._sc_dim, self._font['font'], self._text,  ignore_exception=False)
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
    
    def display_text_cursor(self, surface=None, pos=None):
        '''
        Display the cursor at the correct location.  
        If a surface is specified, display on it, else display on the screen.
        '''
        if surface == None:
            surface = self.screen

        if pos == None:
            to_set_corners = False
            pos = self._sc_pos
        else:
            to_set_corners = True
            self._set_corners(pos=pos)

        # get text dim until cursor position
        width, height = self._font['font'].size(self._text[:self.cursor_place])
        
        # get marges
        x_marge, y_marge = center_text(self._sc_dim, self._font['font'], self._text[:self.cursor_place])
        if not self._centered:
            x_marge = self._rs_marge_text

        # get cursor pos
        x = self.TOPLEFT[0] + width + x_marge
        y_top = self.TOPLEFT[1] + y_marge
        y_bottom = self.BOTTOMLEFT[1] - y_marge

        top_pos = np.array([x, y_top], dtype=int)
        bottom_pos = np.array([x, y_bottom], dtype=int)
        
        if self.is_cursor_displayed:
            pygame.draw.line(surface, C.BLACK, top_pos, bottom_pos, self.CURSOR_WIDTH)
    
        self.change_cursor_state()

        if to_set_corners:
            self._set_corners()

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

    def display(self, surface=None, pos=None):
        '''
        Display the InputText  
        If a surface is specified, display on it, else display on the screen.
        '''

        # set string to be displayed
        if self.is_pretext:
            self.text_color = self.COLOR_PRETEXT
            string = self.pretext

        elif self.cache:
            string = '$' * len(self._text)
            self.text_color = self._base_text_color
        
        else:
            string = self._text
            self.text_color = self._base_text_color

        super().display(text=string, surface=surface, pos=pos)
        
        if self.active:
            self.display_text_cursor(surface=surface, pos=pos)

    def __repr__(self):
        return "InputText Object"


class ScrollList(Form):
    '''
    Scroll List object, take a list of lines, display them in the scroll list box,
    with a scroll bar.  

    The lines can be either a built-in object like: Form, Button, TextBox, ...
    Or a list of multiple of them.  
    In the case of a list, the position of each element will be considered as relative position
    to the line of the element (and not to the whole window).

    Parameters
    ---
    `lines`: list[list]  
    The lines of the instance.

    `bar_color`: tuple  
    The color used for the scroll bar.

    Methods
    ---
    `get_line`: Return the specified line  
    `add_line`: Add a line to the instance  
    `remove_line`: Remove a line from the instance  
    `clear`: Clear the lines of the instance  
    `set_cursor_place`: Set where the cursor is placed (up/down/...)  
    `set_active_state`: Set if an element is active or not  
    `run`: React to user inputs on the scroll bar, call the objects in lines run methods  
    `display`: display the scroll list  
    '''

    def __init__(self, dim, pos, lines, *, color=C.WHITE,
                    scale_dim=True, scale_pos=True, bar_color=C.LIGHT_GREY):
        
        super().__init__(dim, pos, color=color, marge=True,
                scale_pos=scale_pos, scale_dim=scale_dim)
        
        # set specifications
        self.WIDTH_SCROLL_BAR = Spec.WIDTH_SCROLL_BAR

        self._lines = list(lines)
        self._are_actives = [] # bool value for each element: is displayed
        self._bar_color = bar_color

        self._selected = False

        # lines to be removed
        self._to_removes = []

        # all unscaled x positions
        self._rel_positions = []

        # set the total y dimension of the lines
        self._tot_y = 0

        self._set_elements()

        # the position of the cursor in % -> between 0 and ?
        self._cursor_y_per = 0

        # the y limits of the surface to be displayed
        self._top_lim = 0
        self._bottom_lim = self._unsc_dim[1]

        self._set_scroll_bar()

    def __len__(self):
        return len(self._lines)

    def get_line(self, index):
        '''
        Return the specified line.
        '''
        return self._lines[index]

    def add_line(self, line, index=None):
        '''
        Add a line to the scroll list.
        if an index is specified, add the line at the given index.
        '''
        if index == None:
            index = len(self._lines)
        
        # pass line 
        if type(line) != list:
            line = [line]

        self._lines.insert(index, line)

        rel_pos = [element.get_pos() for element in line]
        self._rel_positions.insert(index, rel_pos)

        are_active = [True for element in line]
        self._are_actives.insert(index, are_active)

        # update tot_y, scroll bar
        self._tot_y += line[0].get_dim()[1]

        self._update_scroll_cursor_dim()

    def remove_line(self, index=None, line=None):
        '''
        Remove a line,  
        If `index` is specified remove the line at the given index.  
        If `line` is specified remove the given line.    
        If nothing is specified remove the last line.
        '''
        if line != None:
            if line in self._lines:
                index = self._lines.index(line)
            else:
                raise ValueError("Given line is not part of scroll list.")

        elif index == None:
            index = len(self._lines) - 1
        
        line = self._lines[index]

        # add line to the to_removes ones
        self._to_removes.append(line)

    def _remove_line(self, line):
        '''
        Remove one of the line.
        '''
        if not line in self._lines:
            return
        
        index = self._lines.index(line)

        self._lines.pop(index)

        self._rel_positions.pop(index)
        self._are_actives.pop(index)

        # update tot_y, scroll bar
        self._tot_y -= line[0].get_dim()[1]

        self._update_scroll_cursor_dim()

    def clear(self):
        '''
        Clear the lines of the instance.
        '''
        self._lines = []
        self._rel_positions = []
        self._are_actives = []
        self._tot_y = 0

        self._update_scroll_cursor_dim()

    def set_cursor_place(self, up=False, down=False, percentage: float=None):
        '''
        Set the cursor place, given one of the following arguments:  
        `up`: if `True` the cursor is set on top.  
        `down`: if `True` the cursor is set at the bottom.  
        `percentage`: value `∈ [0, 1]` that specify the position of the cursor; up is 0, down is 1.
        '''
        if up:
            per = 0
        elif down:
            per = 1
        elif percentage != None:
            per = percentage
        else:
            raise ValueError("No argument given.")
            
        y = per * (self._sc_dim[1] - self._scroll_cursor._sc_dim[1])
        y += self._scroll_cursor._sc_dim[1]//2

        self._update_scroll_cursor_pos(mouse_y=y)

    def set_active_state(self, value:bool, idx_line=None, idx_element=None, line=None, element=None):
        '''
        Set if an element is active;
        an active element is displayed and react to user events,  
        given the line/index and the element/index.
        '''
        if idx_line == None:
            if line in self._lines:
                idx_line = self._lines.index(line)
            else:
                return

        if idx_element == None:
            if element in self._lines[idx_line]:
                idx_element = self._lines[idx_line].index(element)
            else:
                return
        
        self._are_actives[idx_line][idx_element] = value

    def run(self, events, pressed):
        '''
        React to the user input,
        update the scroll cursor,
        the displayed part of the list.  
        Execute the `run` function of the elements that have one.
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
            self._update_scroll_cursor_pos()
        
        self._run_elements(events, pressed)

        for line in self._to_removes:
            self._remove_line(line)
        
        self._to_removes = []

    def _run_elements(self, events, pressed):
        '''
        For each element, check if it has a `run` method, and if it's the case, run it.
        '''
        for idx_l, line in enumerate(self._lines):
            for idx_e, element in enumerate(line):
                if hasattr(element, "run") and self._are_actives[idx_l][idx_e]:
                    element.run(events, pressed)

    def _set_elements(self):
        '''
        Pass all lines to list,  
        Set the tot_y attr,  
        Store all relative positions of the elements.
        '''
        self._rel_positions = []
        self._tot_y = 0

        for i, line in enumerate(self._lines):

            # first pass all the lines to list
            if type(line) != list:
                self._lines[i] = [line]

            # get all x pos
            rel_pos = []
            are_active = []

            for element in self._lines[i]:
                rel_pos.append(element.get_pos())
                are_active.append(True)

            self._rel_positions.append(rel_pos)
            self._are_actives.append(are_active)

            # increment the tot_y
            self._tot_y += self._lines[i][0].get_dim()[1]

    def _update_scroll_cursor_dim(self):
        '''
        When a line is added/removed, update the dimension of the cursor.
        '''
        # scroll cursor
        if self._tot_y <= self._unsc_dim[1]:
            dim_y = self._unsc_dim[1]
        else:
            dim_y = self._unsc_dim[1] * (self._unsc_dim[1] / self._tot_y)
        
        dim = (self.WIDTH_SCROLL_BAR, dim_y)
        
        self._scroll_cursor.set_dim(dim, scale=True)

    def _update_scroll_cursor_pos(self, mouse_y=None):
        '''
        Update scroll bar position,  
        if `mouse_y=None`: update its position according to the mouse position,
        else update it given `mouse_y`.  
        Update the limits of the displayed elements.
        '''
        if mouse_y == None:
            mouse_y = pygame.mouse.get_pos()[1]
    
            # add the potential dif pos
            mouse_y -= Dimension.scale(self._scroll_cursor._dif_pos_on_it[1])

        mouse_y = self._y_in_boundaries(mouse_y)

        # update postion
        new_pos = [
            Dimension.scale(self._unsc_dim[0] - self.WIDTH_SCROLL_BAR),
            mouse_y - self._scroll_cursor._sc_dim[1]//2
        ]

        self._scroll_cursor.set_pos(new_pos)

        # update scroll cursor state
        # handeln the marge
        rel_y = mouse_y - self._scroll_cursor._sc_dim[1]//2
        
        self._cursor_y_per = rel_y / self._sc_dim[1]
        
        # update limits
        self._top_lim = (self._tot_y * self._cursor_y_per)
        self._bottom_lim = (self._tot_y * self._cursor_y_per) + self._unsc_dim[1]

    def _y_in_boundaries(self, y):
        '''
        Check if given position (scaled) is in the scroll bar boundaries,
        Return the in boundaries position.
        '''
        top_lim = self._scroll_cursor._sc_dim[1]//2
        bottom_lim = self._sc_dim[1] - self._scroll_cursor._sc_dim[1]//2

        if y < top_lim:
            return top_lim
        
        if y > bottom_lim:
            return bottom_lim
        
        return y

    def _is_selected(self, events):
        '''
        Return if the scroll cursor is selected.  
        Selected means mouse button down and mouse cursor on scroll cursor.
        '''
        if self._scroll_cursor.on_it():
            is_pressed = pygame.mouse.get_pressed()[0]
            return is_pressed

    def _is_still_selected(self, events):
        '''
        Return if the scroll cursor is still selected, meaning if the mouse button is still down.
        '''
        return pygame.mouse.get_pressed()[0]

    @property
    def _dif_pos_on_it(self):
        return self._scroll_cursor._dif_pos_on_it
    
    @_dif_pos_on_it.setter
    def _dif_pos_on_it(self, value):
        '''
        Set the dif_pos_on_it attr on scroll cursor, all elements of instance
        '''
        # check if instance has been initialised
        if not hasattr(self, "_scroll_cursor"):
            return
        
        self._scroll_cursor._dif_pos_on_it = value

        for line in self._lines:
            for element in line:
                element._dif_pos_on_it = value

    def _set_scroll_bar(self):
        '''
        Set the scroll bar: the bar rectangle and the moving cursor.
        '''
        # rectangle bar
        dim = (self.WIDTH_SCROLL_BAR, self._unsc_dim[1])
        
        # set a relative position to the rect bar -> can display on specified position
        rel_pos = (
            self._unsc_dim[0] - self.WIDTH_SCROLL_BAR,
            0
        )
        rect_color = get_dark_color(self._bar_color)

        self._rect_bar = Form(dim, rel_pos, color=rect_color, marge=True)

        # scroll cursor
        if self._tot_y <= self._unsc_dim[1]:
            dim_y = self._unsc_dim[1]
        else:
            dim_y = self._unsc_dim[1] * (self._unsc_dim[1] / self._tot_y)
        
        dim = (self.WIDTH_SCROLL_BAR, dim_y)

        dif_y = self._cursor_y_per * self._unsc_dim[1]
        
        # set a relative position to the scroll cursor -> can display on specified position
        pos = (
            self._unsc_dim[0] - self.WIDTH_SCROLL_BAR, 
            dif_y
        )

        self._scroll_cursor = Form(dim, pos, color=self._bar_color)

        # add dif_pos_on_it to cursor -> it has rel pos
        self._scroll_cursor._dif_pos_on_it = self._unsc_pos.copy()

    def display(self, pos=None):
        '''
        Display the scroll list.
        '''
        # reset surface
        self.set_surface()

        if pos == None:
            pos = self._sc_pos

        y = 0

        for i, line in enumerate(self._lines):

            y_top = y
            y_bottom = y + line[0].get_dim()[1]

            # check if line is displayed
            if y_bottom > self._top_lim and y_top < self._bottom_lim:

                self._display_line(i, y - self._top_lim, base_pos=pos)
                
            y += line[0].get_dim()[1]

        super().display(pos=pos, marge=True)

        abs_pos = (
            pos[0] + self._rect_bar._sc_pos[0],
            pos[1] + self._rect_bar._sc_pos[1]
        )
        self._rect_bar.display(pos=abs_pos)

        abs_pos = (
            pos[0] + self._scroll_cursor._sc_pos[0],
            pos[1] + self._scroll_cursor._sc_pos[1]
        )
        self._scroll_cursor.display(pos=abs_pos)

    def _display_line(self, idx_line, y, base_pos=None):
        '''
        Display a line at the given relative y position.  
        Set in the first place a position relative to
        the scroll list, display the line on the scroll list surface. And then
        set the absolute position, to be able to use on_it function
        '''
        surface = self.get_surface('main')

        for idx_ele in range(len(self._lines[idx_line])):

            rel_pos = self._rel_positions[idx_line][idx_ele]
            element = self._lines[idx_line][idx_ele]
            is_active = self._are_actives[idx_line][idx_ele]

            if not is_active:
                continue

            # set the relative position -> display on scoll list surface    
            rel_pos = Dimension.scale([rel_pos[0], rel_pos[1] + y])

            element.display(surface=surface, pos=rel_pos)

            # set the absolute position -> on_it function
            abs_pos = [
                base_pos[0] + rel_pos[0],
                base_pos[1] + rel_pos[1]
            ]
            
            element.set_pos(abs_pos)
    
    def __repr__(self):
        return "ScrollList Object"