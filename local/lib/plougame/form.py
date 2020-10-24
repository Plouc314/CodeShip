import pygame
from .helper import mean, rl, get_dark_color, get_light_color
from .aux import Dimension, Font, C
from .spec import Specifications as Spec

class Form:
    '''
    Base object of the module, extension of pygame Surface object  
    Form's dimension and position are auto rescaled when window is rescaled  
    Form can take either a color, in that case the Form's surface will be uni-color, or a custom surface (can have a colored font)  

    Methods:
        - display : display the instance on the Interface's screen
        - delete : for when the instance is no longer used, increase performance
        - set_pos : set a new position for the object
        - set_dim_pos : set new position and dimension, keep the same surface
        - set_surf : set a new surface, can be a pygame surface or a numpy.ndarray
        - set_marge_width : set a new marge width
        - set_color : set a new color to uni-color surface or font
        - on_it : return if the mouse is on the Form's surface
        - rotate : rotate the surface of a given angle
        - compile : return  a pygame.Surface object of the instance
        - get_mask : return a pygame.mask.Mask object of the instance
    '''
    screen = None
    _interface = None

    MARGE_WIDTH = Spec.MARGE_WIDTH
    MARGE_TEXT = Spec.MARGE_TEXT

    _dev_rotation = (0,0)
    
    def __init__(self, dim, pos, color=C.WHITE, *, rescale=True, scale_pos=True, 
                scale_dim=True, center=False, surface=None, with_font=False, marge=False):
        
        self._set_dim_attr(dim, scale=scale_dim, update_surf=False)

        self.set_pos(pos, scale=scale_pos, center=center)
        
        self.color = color
    
        self.set_surface(surface, with_font=with_font)
        
        # set marges
        self._rs_marge_width = Dimension.E(self.MARGE_WIDTH)
        self._rs_marge_text = Dimension.E(self.MARGE_TEXT)

        if marge: # has to be done after set_surf -> must have a surf set
            self._set_high_color()
            self.marge_color = self._high_color

        if rescale:
            # add every gui obj to interface to be able to rezise gui objs auto
            self._interface.gui_objects.append(self)

    def delete(self):
        '''
        Remove the instance from Interface's references, it won't be resized anymore.
        '''
        self._interface.gui_objects.remove(self)

    def set_surface(self, surface=None, with_font=False):
        '''
        Set the surface attribute, 
        
        a dict: main surface, original surface (when custom), font surface (optional), surface type (intern purposes)
        
        Arguments:
            surface : can be either a pygame.Surface or numpy.ndarray object
            with_font : if a custom surface is set & is partly transparent & with_font=True, the blanks will be filled with the COLOR attribute
            note : if surface not specified, set a uni-color surface with the current COLOR attribute
        '''

        # dict with type, original surf, main surf, font surf
        self._surf = {}
        
        if surface is None:
            # by default: create a uni-colored surface
            self._surf['type'] = 'default'
            self._surf['original'] = pygame.Surface(rl(self._unsc_dim), pygame.SRCALPHA)
            self._surf['main'] = pygame.Surface(rl(self._sc_dim), pygame.SRCALPHA)
            self._surf['main'].fill(self.color)
            self._surf['original'].fill(self.color)
       
        elif type(surface) == pygame.Surface:
            # if custom surface: keep a original surf to rescale properly
            self._surf['type'] = 'custom'
            self._surf['original'] = surface
            self._surf['main'] = pygame.transform.scale(surface, rl(self._sc_dim))
       
        else:
            # numpy array
            self._surf['type'] = 'custom'
            self._surf['original'] = pygame.surfarray.make_surface(surface)
            self._surf['main'] = pygame.transform.scale(self._surf['original'], rl(self._sc_dim))

        # if defined set font surfs
        self._surf['font'] = None
        if with_font:
            self._surf['font'] = pygame.Surface(rl(self._sc_dim))
            try:
                self._surf['font'].fill(self.color)
            except:
                self._surf['font'] = None # reset font

    def get_surface(self, surf_type):
        '''
        Return the specified surface,  
        can be:
        - original: the unscaled & unrotated surface
        - main: the scaled & rotated main displayed surface
        - font: if set, the font surface
        '''
        return self._surf[surf_type]

    def rotate(self, angle: int, *, rotate_font=True):
        '''
        Rotate the main surface of a given angle (degree).  
        The original surface isn't touched, to keep sharpness.
    
        Args: rotate_font: if a font as been specified, if it has to be rotated
        '''
        if angle == 0:
            return # potentially more efficient
    
        new_main = pygame.transform.scale(self._surf['original'], rl(self._sc_dim))

        # get none rotated center
        x1, y1 = new_main.get_rect().center

        # rotate surf
        self._surf['main'] = pygame.transform.rotate(new_main, angle)
    
        # get rotated center
        x2, y2 = self._surf['main'].get_rect().center
    
        # get deviation between the two centers
        dx = x2 - x1
        dy = y2 - y1
        # store the dev rotation -> in case of set_pos
        self._dev_rotation = Dimension.inv_scale((dx, dy))

        # call _set_pos_attr -> it auto compensate the rotation
        # doesn't update unscaled_pos -> keep an anchor point
        self._set_pos_attr(self._sc_pos, update_original=False, compensate_rotation=True)
    
        if self._surf['font'] and rotate_font:
            self._surf['font'] = pygame.transform.rotate(pygame.Surface(rl(self._sc_dim), pygame.SRCALPHA), angle)
            self._surf['font'].fill(self.color)

    def get_mask(self, *, scale=True, with_marge=False, with_font=False):
        '''
        Return a pygame.mask.Mask object of the Form.

        Arguments:
            - scale : if the created mask is scaled to the current window's dimension
            - with_marge : if the marges are included in the mask
            - with_font : if the font is included in the mask
        '''
        surf = self.compile(scale=scale, with_marge=with_marge, with_font=with_font, extend_dim=with_marge)

        return pygame.mask.from_surface(surf)

    def _set_dim_attr(self, dim, *, scale=False, update_original=True, update_surf=True):
        '''
        Set a new dimension.  

        Arguments:
            - scale : if the dimension needs to be scaled to the current windows dimension  
            - update_original : if the unscaled dimension attribute is also modified
            - update_surf : if the surface attributes are updated
        '''
        if scale:
            self._sc_dim = Dimension.scale(dim)
        
            if update_original:
                self._unsc_dim = list(dim)
        
        else:
            self._sc_dim = list(dim)
        
            if update_original:
                self._unsc_dim = Dimension.inv_scale(dim)
        
        if update_surf:
            self._rescale_surf()
    
    def _set_pos_attr(self, pos, *, scale=False, compensate_rotation=False, update_original=True):
        '''
        Set a new position.  

        Arguments:
            - scale : if the position needs to be scaled to the current windows dimension  
            - compensate_rotation : when the Form has been rotated, if the new position take account of the rotation
              deviation
            - update_original : if the unscaled position attribute is also modified
        '''
        if scale:
            
            if update_original:
                self._unsc_pos = list(pos)
            
            if compensate_rotation:
                # add potential deviation -> if rotation occured
                pos = Dimension.scale(self._unsc_pos)
                dev = Dimension.scale(self._dev_rotation)
                self._sc_pos = [pos[0] - dev[0], pos[1] - dev[1]]
            else:
                self._sc_pos = Dimension.scale(pos)
            
        else:
            
            if update_original:
                self._unsc_pos = Dimension.inv_scale(pos)
            
            if compensate_rotation:
                # add potential deviation -> if rotation occured
                pos = Dimension.scale(self._unsc_pos)
                dev = Dimension.scale(self._dev_rotation)
                self._sc_pos = [pos[0] - dev[0], pos[1] - dev[1]]
            else:
                self._sc_pos = list(pos)

    def set_marge_width(self, width: int, *, scale=False):
        '''
        Set the width of the marge  
        
        Arguments:
            - scale : if the width needs to be rescaled to the current window's dimension
        '''
        if scale:
            self.MARGE_WIDTH = width
            self._rs_marge_width = Dimension.E(width)
        else:
            self.MARGE_WIDTH = Dimension.inv_scale(width)
            self._rs_marge_width = round(width)

    def set_color(self, color: tuple, *, marge=False):
        '''
        Set the color of the surface

        Arguments:
            - marge : set to True if the object as marge
        '''
        # if has custom surf -> change font color, else change normal color
        if self._surf['font'] == None:
            self._surf['main'].fill(color)
        else:
            self._surf['font'].fill(color)
        
        self.color = color
        
        if marge:
            self._set_high_color()
            self.marge_color = self._high_color

    def _set_high_color(self):
        '''
        Set the color taken by the marges and the object when highlighted.
        '''
        if mean(self.color) < 130:
            self._high_color = get_light_color(self.color)
        
        else:
            self._high_color = get_dark_color(self.color)

    def display_margin(self, surface):
        pygame.draw.line(surface, self.marge_color, self.TOPLEFT   , self.TOPRIGHT   , self._rs_marge_width)
        pygame.draw.line(surface, self.marge_color, self.TOPLEFT   , self.BOTTOMLEFT , self._rs_marge_width)
        pygame.draw.line(surface, self.marge_color, self.TOPRIGHT  , self.BOTTOMRIGHT, self._rs_marge_width)
        pygame.draw.line(surface, self.marge_color, self.BOTTOMLEFT, self.BOTTOMRIGHT, self._rs_marge_width)

    def display(self, *, surface=None, pos=None, marge=False):
        '''
        Display the Form
        
        Arguments:
            surface : can specify the surface to display on, by the default: the window screen
            pos : can specify position where the form is displayed
            marge : if the marges are also displayed
        '''

        if surface is None:
            surface = self.screen

        if pos is None:
            pos = rl(self._sc_pos)
        else:
            pos = rl(pos)
        
        # order of display : 1) font 2) main 3) marge
        if self._surf['font']:
            surface.blit(self._surf['font'], pos)

        surface.blit(self._surf['main'], pos)
        
        if marge:
            self.display_margin(surface)
    
    def on_it(self):
        '''Return if the mouse is on the surface (not rotated)'''
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.TOPLEFT[0] and mouse_pos[0] < self.TOPRIGHT[0]:
            if mouse_pos[1] > self.TOPLEFT[1] and mouse_pos[1] < self.BOTTOMLEFT[1]:
                return True
        return False

    def set_corners(self):
        self.TOPLEFT = rl(self._sc_pos)
        self.TOPRIGHT = rl(self._sc_pos[0]+self._sc_dim[0],self._sc_pos[1])
        self.BOTTOMLEFT = rl(self._sc_pos[0], self._sc_pos[1]+self._sc_dim[1])
        self.BOTTOMRIGHT = rl(self._sc_pos[0]+self._sc_dim[0],self._sc_pos[1]+self._sc_dim[1])

    def get_center(self, scale=False, fp=5):
        '''
        Return the position of the center of the form

        Arguments:
            - scale : if the center is scaled to the current window dimension
            - fp : the floating point
        '''
        x, y = self._surf['main'].get_rect().center
        x, y = Dimension.inv_scale((x,y))
        # patch rotation deviation
        x -= self._dev_rotation[0]
        y -= self._dev_rotation[1]
        # add position -> get absolute position
        x += self._unsc_pos[0]
        y += self._unsc_pos[1]

        if scale:
            x,y = Dimension.scale((x,y))

        return [x,y]

    def _rescale_surf(self):
        '''
        Rescale the surf attribute to the current dimension.  
        '''
        
        if self._surf['type'] == 'default':
            self._surf['main'] = pygame.Surface(rl(self._sc_dim))
            self._surf['main'].fill(self.color)
        else:
            self._surf['main'] = pygame.transform.scale(self._surf['original'], rl(self._sc_dim))
        
        if self._surf['font']:
            self._surf['font'] = pygame.Surface(rl(self._sc_dim))
            self._surf['font'].fill(self.color)

    def set_pos(self, pos, *, center=False, scale=False):
        '''Set a new position
        
        Arguments:
            - pos : the new position
            - center : if true, the form will be centered on the new pos, else the new pos is the top left of the obj
            - scale : if the position needs to be rescaled to the current window's dimension
        '''
        pos = list(pos)

        # check if the surface has been rotated
        is_rotated = any(self._dev_rotation)

        if not center:
            self._set_pos_attr(pos, scale=scale, compensate_rotation=is_rotated)
            self.set_corners()
        else:
            if scale:
                pos = Dimension.scale(pos)

            pos = [pos[0]-self._sc_dim[0]/2, pos[1]-self._sc_dim[1]/2]
            self._set_pos_attr(pos, compensate_rotation=is_rotated)
            self.set_corners()

    def set_dim_pos(self, dim, pos, *, scale_dim=False, scale_pos=False, update_original=True):
        '''
        Reset dimension & position of form
        
        Arguments:
            - dim, pos : new dimension, position
            - scale_dim/pos : if new dim/pos need to be scaled to current window's dimension
            - update_original : if new dim/pos are kept when window is resized
        '''
        self._set_dim_attr(dim, scale=scale_dim, update_original=update_original)
        self._set_pos_attr(pos, scale=scale_pos, update_original=update_original)
        self.set_corners()

    def compile(self, *, scale=False, with_marge=True, with_font=True, extend_dim=False):
        '''
        Compile all the elements of the instance into one pygame.Surface object.  
        Return a pygame.Surface object.  

        Arguments:
            - scale : if created surface is scaled to the current window's dimension
            - with_marge : if the marges are added to the surface
            - with_font : when the instance has a font (custom surface), if True: add the font to the surface
            - extend_dim : if True & with_marge=True, adapt the surface's dimension to fit in the entire marges
        '''
        # adapt every value / surface according to scale parameter
        if scale:
            dim_attr = self._sc_dim
            marge_width = self._rs_marge_width
            surf_main = self._surf['main']
        
            if with_font:
                surf_font = self._surf['font']

        else:
            dim_attr = self._unsc_dim
            marge_width = self.MARGE_WIDTH
            surf_main = self._surf['original']

            if with_font:
                # create font surf
                surf_font = pygame.Surface(rl(self._unsc_dim))
                surf_font.fill(self.color)

        # create the base - a transparent surface
        if with_marge and extend_dim:
            # take the marge width into account to create the base surface
            dim = (dim_attr[0] + marge_width, dim_attr[1] + marge_width)
            dif_pos = marge_width//2 # put all the elements according to the extended surface
        else:
            dim = dim_attr
            dif_pos = 0
        
        surface = pygame.Surface(dim, pygame.SRCALPHA)

        if self._surf['font'] != None and with_font:
            surface.blit(surf_font, (dif_pos, dif_pos))
        
        surface.blit(surf_main, (dif_pos, dif_pos))

        if with_marge: # display every marge
            # create corners
            topleft = (dif_pos, dif_pos)
            topright = (dim_attr[0] + dif_pos, dif_pos)
            bottomleft = ((dif_pos, dim_attr[1] + dif_pos))
            bottomright = ((dim_attr[0] + dif_pos, dim_attr[1] + dif_pos))
            # draw the marge
            pygame.draw.line(surface, self.marge_color, topleft   , topright   , marge_width)
            pygame.draw.line(surface, self.marge_color, topleft   , bottomleft , marge_width)
            pygame.draw.line(surface, self.marge_color, topright  , bottomright, marge_width)
            pygame.draw.line(surface, self.marge_color, bottomleft, bottomright, marge_width)

        return surface