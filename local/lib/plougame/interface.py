import pygame
from pygame.locals import *
from .form import Form
from .aux import Dimension, Font, C
from .helper import rl
from .spec import Specifications as Spec


class Interface:
    '''
    Manage the window and all the gui objects (Form, Button, ...), update the screen and mangae the fps.
    The window always appear in fullscreen (to be fixed), the window can be resized and all objects will be rescaled auto.

    Work with pygame, screen object store as an attribute. So can create own pygame object and add them to the Interface using .add_resizable_objects.

    Must be setup (using .setup method) before be used.

    Methods:
        - setup : Initialize the module, create the window
        - add_resizable_objects : Add custom objects to be rescaled auto by Interface
        - run : update the screen, get the input for current frame, check for quit events...
    '''
    clock = pygame.time.Clock()
    running = True
    gui_objects = [] # all gui objects, ex: button, form...
    resize_objects = [] # must have a on_resize(self, factor) method

    @classmethod
    def setup(cls, dim: (int, int), win_title: str, *, font_color=C.WHITE):
        '''
        Arguments:
            - dim : default window dimension, used to set other object's dimension
            - win_title : the title of the window
            - font_color : the default color of the window
        '''
        
        # setup Dimension
        Dimension.set_dim(dim)

        cls.font_color = font_color
        
        # create screen in full screen dimension: resize to specified dim

        infoObject = pygame.display.Info()
        x, y = infoObject.current_w, infoObject.current_h
        fullscreen_dim = rl(Dimension.scale((x, y), factor=.96))

        cls.screen = pygame.display.set_mode(fullscreen_dim, HWSURFACE|DOUBLEBUF|RESIZABLE)
        cls.screen.fill(cls.font_color)
        pygame.display.set_caption(win_title)

        cls.set_screen(cls.screen)

        # set references to Form object
        Form._interface = cls
        Form.screen = cls.screen

        cls.x_padding = Form((0,0),(0,0),cls.font_color, rescale=False)
        cls.y_padding = Form((0,0),(0,0),cls.font_color, rescale=False)

        # rescale window to correct dim
        cls.rescale(fullscreen_dim)
        
    @classmethod
    def set_screen(cls, screen):
        '''Set a pygame sreen object'''

        for gui_obj in cls.gui_objects:
            gui_obj.screen = screen

    @classmethod
    def add_resizable_objs(cls, objects: list):
        '''
        Object's method on_rezise(self, scale_factor) will be called when window is rezised
        
        scale_factor: factor of dimension compared to initial dimension
        '''
        # resize a first time
        for obj in objects:
            # check that each object has a on_resize method, else: don't add obj to resizable ones
            if hasattr(obj, 'on_resize'):
                obj.on_resize(Dimension.f)
                cls.resize_objects.append(obj)
            else:
                print('WARNING: resizable objects must have an on_resize(self, scale_factor) method')

    @classmethod
    def rescale(cls, new_dim):

        # set new scale factor
        scale_factor = min(new_dim[0]/Dimension.x, new_dim[1] / Dimension.y)

        Dimension.f = scale_factor

        win_x, win_y = Dimension.get_window_dim()

        # create padding to fill blank space
        dim_px = [new_dim[0] - win_x, win_y]
        
        if dim_px[0] > 0:
            pos = [win_x, 0]
            cls.x_padding.set_dim_pos(dim_px, pos, update_original=False)
        
        dim_py = [win_x, new_dim[1] - win_y]
        
        if dim_py[1] > 0:
            pos = [0, win_y]
            cls.y_padding.set_dim_pos(dim_py, pos, update_original=False)

        # resize every objects
        for gui_obj in cls.gui_objects:
            
            # resize dimension
            gui_obj.set_dim_pos(gui_obj._unsc_dim, gui_obj._unsc_pos, 
                        scale_pos=True, scale_dim=True, update_original=False)
            
            # resize marges
            gui_obj._rs_marge_width = Dimension.E(gui_obj.MARGE_WIDTH)
            gui_obj._rs_marge_text = Dimension.E(gui_obj.MARGE_TEXT)

            # rezise existing fonts
            if hasattr(gui_obj, 'font'):
                fontsize = gui_obj.font['size']
                gui_obj.font = Font.f(fontsize)

        for rz_obj in cls.resize_objects:
            rz_obj.on_resize(scale_factor)

    @classmethod
    def run(cls, fill=True):
        '''
        Execute once a frame
        Update the screen, get the input for current frame, check for quit events...
        Return:
            - pressed : pygame object
            - events : pygame object
        '''
        cls.x_padding.display()
        cls.y_padding.display()
        
        cls.clock.tick(Spec.FPS)
        
        pygame.display.update()

        if fill:
            cls.screen.fill(cls.font_color)

        pressed = pygame.key.get_pressed()
        events = pygame.event.get()

        cls.mouse_pos = pygame.mouse.get_pos()

        for event in events:
            # check quit
            if event.type == pygame.QUIT:
                cls.running = False
            # check window resize
            if event.type == VIDEORESIZE:
                cls.rescale(event.dict['size'])
                
        if pressed[pygame.K_ESCAPE]:
            cls.running = False

        return pressed, events