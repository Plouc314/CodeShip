import pygame
from .form import Form
from .helper import Delayer, center_text, get_pressed_key, rl
from .aux import Font, C
from .spec import Specifications as Spec

class Cadre(Form):
    def __init__(self, dim, pos, color=C.WHITE, *, set_transparent=False, scale_dim=True, scale_pos=True):
        
        super().__init__(dim, pos, color, scale_dim=scale_dim, scale_pos=scale_pos, marge=True)
        
        self.set_corners()
        self.is_transparent = set_transparent
        if set_transparent:
            self.surf['main'].set_colorkey(color)

    def rescale_surf(self):
        # overwrite rescale method to keep the cadre transparent when rescaling
        super().rescale_surf()
        if self.is_transparent:
            self.surf['main'].set_colorkey(self.COLOR)

    def display(self):
        super().display(marge=True)

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

        self.text = text
        
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

    def highlight(self):
        '''
        Set the highlight color on surf, if custom surf with font: set highlight on surf font
        '''
        if self.on_it():
            # check if custom surf & font or normal unicolor
            if self.surf['type'] == 'custom':
                if self.surf['font']: # check if has a font
                    self.surf['font'].fill(self.high_color)
                else:
                    self.surf['main'].fill(self.high_color)
            else:
                self.surf['main'].fill(self.high_color)
        else:
            # check if custom surf
            if self.surf['type'] == 'custom':
                if self.surf['font']: # check if has a font
                    self.surf['font'].fill(self.COLOR)
                else:
                    self.surf['main'] = pygame.transform.scale(self.surf['original'], rl(self.dim))
            else:
                self.surf['main'].fill(self.COLOR)
                
    def display(self):
        # if highlight actived, handeln highlight color changes
        if self.highlighted:
            self.highlight()
        
        # display the surf
        super().display(marge=True)
        
        # dusplay the text with marges
        if self.text: # check that there is text
            x_marge, y_marge = center_text(self.dim, self.font['font'], self.text)
            if not self.centered:
                x_marge = self.rs_marge_text
            font_text = self.font['font'].render(self.text,True,self.text_color)
            self.screen.blit(font_text,rl(self.pos[0]+x_marge,self.pos[1]+y_marge))

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
        
        self.text = text
        self.centered = centered
        self.font = font
        self.lines = text.split('\n')
        self.text_color = text_color
        self.set_corners()
        self.as_marge = marge
        if marge:
            self.set_highlight_color()
            self.MARGE_COLOR = self.high_color

    def set_text(self, text):
        ''' Set the text of the TextBox'''
        self.text = text
        self.lines = text.split('\n')

    def display(self):
        '''
        Display the TextBox
        '''
        super().display(marge=self.as_marge)

        # split the box in n part for n lines
        y_line = round(self.dim[1]/len(self.lines))
        for i, line in enumerate(self.lines):
            x_marge, y_marge = center_text((self.dim[0],y_line), self.font['font'], line)
            if not self.centered:
                x_marge = self.rs_marge_text
            font_text = self.font['font'].render(line,True,self.text_color)
            self.screen.blit(font_text,rl(self.pos[0]+x_marge,self.pos[1]+i*y_line+y_marge))

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
    bool_cursor = True
    
    def __init__(self, dim, pos, color=C.WHITE, text='', *, text_color=C.BLACK, centered=False, font=Font.f(30),
                    limit=None, cache=False, scale_dim=True, scale_pos=True, pretext=None):

        super().__init__(dim, pos, color, text_color=text_color, centered=centered, font=font, scale_dim=scale_dim, scale_pos=scale_pos)
        
        self.active = False
        self.cursor_place = len(text)
        self.limit = limit # max char
        self.cache = cache # if true text -> ***
        self.pretext = pretext # if something: add a text that disapear when active
        # text: text that is display
        # content: text that is input
        self.set_text(text, with_pretext=self.pretext)
    
    def set_text(self, text, with_pretext=False):
        text = str(text)
        self.content = text
        self.cursor_place = len(text)
        if with_pretext:
            self.text = self.pretext
        else:
            if self.cache:
                self.text = '$' * len(self.content)
            else:
                self.text = self.content

    @get_input_deco
    def is_moving_left(self, pressed):
        if pressed[pygame.K_LEFT]:
            return True

    @get_input_deco
    def is_moving_right(self, pressed):
        if pressed[pygame.K_RIGHT]:
            return True

    @get_input_deco
    def get_input(self, events, pressed):
        self.active = True
        
        # check for end active
        if pressed[pygame.K_RETURN]:
            self.active = False
            self.highlighted = False
            return False
        elif not self.on_it():
            pushed = False
            for event in events:
                if event.type == pygame.MOUSEBUTTONUP:
                    pushed =  True 
            if pushed:
                self.active = False
                self.highlighted = False
                return False

        # check for new char
        key = get_pressed_key(pressed)
        if key:
            self.content = self.content[:self.cursor_place] + key + self.content[self.cursor_place:]
            self.cursor_place += 1
            if self.limit:
                if len(self.content) > self.limit:
                    self.content = self.content[:-1]
                    self.cursor_place -= 1
                
            try:
                center_text(self.dim, self.font['font'], self.content,  execption=True)
            except ValueError:
                self.content = self.content[:-1]
                self.cursor_place -= 1
            return True
        
        # check for char deletion
        if pressed[pygame.K_BACKSPACE]:
            self.content = self.content[:self.cursor_place-1] + self.content[self.cursor_place:]
            self.cursor_place -= 1
            return True
    
        # check for cursor change
        if self.is_moving_left(pressed):
            if self.cursor_place > 0:
                self.cursor_place -= 1
        
        if self.is_moving_right(pressed):
            if self.cursor_place < len(self.content):
                self.cursor_place += 1

        if self.cache:
            self.text = '$' * len(self.content)
        else:
            self.text = self.content

        return False
    
    def display_text_cursor(self):
        width, height = self.font['font'].size(self.text[:self.cursor_place])
        x_marge, y_marge = center_text(self.dim, self.font['font'], self.text[:self.cursor_place])
        if not self.centered:
            x_marge = self.rs_marge_text

        bottom_pos = rl(self.TOPLEFT[0] + x_marge + width, self.BOTTOMLEFT[1]-y_marge)
        top_pos = rl(self.TOPLEFT[0] + x_marge + width, self.TOPLEFT[1]+y_marge)
        
        if self.bool_cursor:
            pygame.draw.line(self.screen, C.BLACK, top_pos, bottom_pos, self.CURSOR_WIDTH)
        self.change_cursor_state()

    @cursor_deco
    def change_cursor_state(self):
        self.bool_cursor = not self.bool_cursor
        return True

    def run(self, events, pressed):
        if self.pushed(events):
            self.active = True
            # if pretext, remove pretext
            if self.pretext:
                self.set_text(self.content)
        
        if self.active:
            self.highlighted = True
            self.display_text_cursor()
            self.get_input(events, pressed)
