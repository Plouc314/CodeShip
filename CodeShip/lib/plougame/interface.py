import pygame
from pygame.locals import *
from .form import Form
from .auxiliary import Dimension, Font, C
from .helper import rl
from .spec import Specifications as Spec
import time

class Interface:
    '''
    Manage the window and all the gui objects (Form, Button, ...), update the screen
    and mangae the fps. The window can be resized and all objects will be rescaled auto.

    Work with pygame, screen object store as an attribute. So can create own pygame object
    and add them to the Interface using .add_resizable_objects.

    Must be setup (using .setup method) before be used.

    Methods:
        - setup : Initialize the module, create the window
        - add_resizable_objects : Add custom objects to be rescaled auto by Interface
        - run : update the screen, get the input for current frame, check for quit events...
    '''
    clock = pygame.time.Clock()
    running = True

    _gui_objects = [] # all gui objects, ex: button, form...
    _subpages = [] # SubPages instances
    _resize_objects = [] # must have a on_resize(self, factor) method

    stats_display = 0
    stats_ndisplay = 0

    @classmethod
    def setup(cls, dim: (int, int), title: str, *, fullscreen=False,
            background_color=C.WHITE, static=False):
        '''
        Arguments:
            - dim : default window dimension, used to set other object's dimension
            - title : the title of the window
            - background_color : the default color of the window
            - static
        '''
        
        # setup Dimension
        Dimension.set_dim(dim)

        cls.background_color = background_color
        cls._is_static = static

        # static interfaces
        cls._n_first_frames = Spec.N_FIRST_FRAMES
        cls._is_active_current_frame = True 

        # create screen
        if fullscreen:
            dim = cls._get_screen_dim()
        
        cls.screen = pygame.display.set_mode(dim, HWSURFACE|DOUBLEBUF|RESIZABLE)
        cls.screen.fill(cls.background_color)
        cls.set_screen(cls.screen)

        pygame.display.set_caption(title)

        # set references to Form object
        Form._interface = cls
        Form.screen = cls.screen

        cls.x_padding = Form((0,0),(0,0),cls.background_color, rescale=False)
        cls.y_padding = Form((0,0),(0,0),cls.background_color, rescale=False)

        # rescale window to correct dim
        cls._rescale(dim)
        
    @classmethod
    def set_screen(cls, screen):
        '''Set a pygame sreen object'''

        for gui_obj in cls._gui_objects:
            gui_obj.screen = screen

    @classmethod
    def set_type(cls, type):
        '''
        Set the type of the interface, can be either static or dynamic
        '''
        if type == "static":
            cls._is_static = True
            cls._n_first_frames = Spec.N_FIRST_FRAMES
        else:
            cls._is_static = False

    @classmethod
    def is_static(cls):
        '''Return if the Interface is static, if not, it is dynamic'''
        return cls._is_static

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
                obj.on_resize(Dimension.get_factor())
                cls._resize_objects.append(obj)
            else:
                print('WARNING: resizable objects must have an on_resize(self, scale_factor) method')

    @classmethod
    def is_frame_displayed(cls):
        '''
        Return if the current frame is displayed, (for static interface case)
        '''
        return cls._is_active_current_frame

    @classmethod
    def set_frame_to_display(cls):
        '''Set the current frame to be displayed'''
        cls._is_active_current_frame = True

    @classmethod
    def run(cls, fill=True):
        '''
        Execute once a frame
        Update the screen, get the input for current frame, check for quit events...
        Return:
            - pressed : pygame object (pygame.key.get_pressed)
            - events : pygame object (pygame.event.get)
        '''
        cls.clock.tick(Spec.FPS)

        pressed = pygame.key.get_pressed()
        events = pygame.event.get()

        is_resize = cls._react_basic_inputs(pressed, events)

        if not cls._is_static:
            # dynamic interface
            cls._display(fill=fill, update=(not is_resize))

            return pressed, events
        
        # static interface

        # display
        if cls._is_active_current_frame:
            cls._is_active_current_frame = False
            cls.stats_display += 1

            cls._display(fill=fill, update=(not is_resize))
            
        else:
            cls.stats_ndisplay += 1

        # react events
        if cls._is_static and cls._is_inputs(pressed, events):
            cls._is_active_current_frame = True

        # the first times display all components of the gui on the screen
        if cls._n_first_frames > 0:
            cls._n_first_frames -= 1
            cls._is_active_current_frame = True

        return pressed, events

    @classmethod
    def _rescale(cls, new_dim):

        # set new scale factor
        scale_factor = min(new_dim[0] / Dimension.get_x(), 
                           new_dim[1] / Dimension.get_y())

        Dimension.set_factor(scale_factor)

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
        for gui_obj in cls._gui_objects:
            
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

        # replace subpages
        for subpage in cls._subpages:
            subpage._sc_pos = Dimension.scale(subpage._unsc_pos)

        for rz_obj in cls._resize_objects:
            rz_obj.on_resize(scale_factor)

    @classmethod
    def _display(cls, fill=True, update=True):
        '''
        Fill the basic screen, display the margins, all pygame.Surface blited on screen.
        '''
        cls.x_padding.display()
        cls.y_padding.display()

        if update:
            pygame.display.update()

        if fill:
            cls.screen.fill(cls.background_color)

    @classmethod
    def _react_basic_inputs(cls, pressed, events) -> bool:
        '''
        React to the basic user inputs such as window resize or quit event.  
        Return if the window has been resized.
        '''
        is_resize = False
        for event in events:
            # check quit
            if event.type == pygame.QUIT:
                cls.running = False
            # check window resize
            if event.type == VIDEORESIZE:
                cls._rescale(event.dict['size'])
                is_resize = True
                
        if pressed[pygame.K_ESCAPE]:
            cls.running = False

        return is_resize

    @classmethod
    def _is_inputs(cls, pressed, events):
        '''
        Check if user has given important inputs, such as clicks...
        '''
        # check if at least one of the inputs has been pressed
        for event in events:
            if event.type != pygame.MOUSEMOTION:
                return True

        # NOTE: look what pressed[300] stands for
        # idx 300 is always true -> set it to false
        pressed = list(pressed)
        pressed[300] = 0

        if any(pressed):
            return True

        return False
    
    @classmethod
    def _get_screen_dim(cls):
        '''
        Return the dimension of the screen.
        '''
        infoObject = pygame.display.Info()
        return infoObject.current_w, infoObject.current_h