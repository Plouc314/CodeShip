import pygame

class Dimension:
    _f = 1

    @classmethod
    def set_factor(cls, factor):
        '''
        Set the scale factor, used to change the dimension of the window 
        (based on the dimension given in `Interface.setup`).
        '''
        cls._f = factor

        # update scaled sizes
        cls._rx = cls._f * cls._x
        cls._ry = cls._f * cls._y

    @classmethod
    def get_factor(cls):
        ''' Return the scale factor. '''
        return cls._f

    @classmethod
    def set_dim(cls, dim):
        '''
        Set the window dimension.
        '''
        cls.WINDOW = dim 
        
        # unscaled
        cls.center_x = int(dim[0]/2)
        cls.center_y = int(dim[1]/2)
        cls.center = (cls.center_x, cls.center_y)
        cls._x = dim[0]
        cls._y = dim[1]
        cls._rx = cls._f * cls._x
        cls._ry = cls._f * cls._y

    @classmethod
    def get_x(cls, scaled=False):
        '''
        Return the x dimension of the window,
        if `scaled=True` the dimension will be scaled to the current window's dimension.
        '''
        if scaled:
            return cls._rx
        else:
            return cls._x

    @classmethod
    def get_y(cls, scaled=False):
        '''
        Return the y dimension of the window,
        if `scaled=True` the dimension will be scaled to the current window's dimension.
        '''
        if scaled:
            return cls._ry
        else:
            return cls._y

    @classmethod
    def get_window_dim(cls):
        '''Return the scaled dimension of the window'''
        return cls.scale(cls.WINDOW)

    @classmethod
    def scale(cls, x, factor=None, fp=5):
        
        if factor:
            f = factor
        else:
            f = cls._f

        # check if x is iterable
        try:
            iter(x)
        
        except TypeError: # not iterable            
            x = round(x*f, fp)

        else: # iterable
            x = list(x)
            for i in range(len(x)):
                x[i] = round(x[i]*f, fp)
            
        return x

    @classmethod
    def inv_scale(cls, x, fp=5):
        '''
        Inverse the scale of the number: scale -> unscale ( note: unscale -> ?!@#@ )

        Arguments:
            - fp : floating point of the unscaled number (to keep precision)

        '''
        f = 1/cls._f
        if type(x) == list or type(x) == tuple:
            x = list(x)
            for i in range(len(x)):
                x[i] = round(x[i]*f, fp)
        else:
            x = round(x*f, fp)
        return x

    @classmethod
    def E(cls, x, *, fp=None):
        return round(x*cls._f, fp)

class C:
    '''Container of predefined colors'''
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    
    LIGHT_BLUE = (135,206,250)
    BLUE = (65,105,225)
    DARK_BLUE = (7, 19, 134)
    
    GREY = (150,150,150)
    LIGHT_GREY = (200,200,200)
    XLIGHT_GREY = (230,230,230)
    
    LIGHT_RED = (255, 80, 80)
    RED = (225, 50, 50)
    DARK_RED = (195, 20, 20)

    LIGHT_GREEN = (124,252,100)
    GREEN = (94,222,70)
    DARK_GREEN = (17, 159, 26)
    
    LIGHT_BROWN = (225, 167, 69)
    
    DARK_PURPLE = (140, 17, 159)
    PURPLE = (180, 57, 199)
    LIGHT_PURPLE = (210, 87, 229)
    
    YELLOW = (253, 240, 49)

class Font:
    '''Create pygame fonts, use .f method'''
    fontname = 'Arial'
    @classmethod
    def f(cls, size):
        '''Create a font of the given size: `{'size':size,'font':pygame.font}`'''
        return {'size':size , 'font':pygame.font.SysFont(cls.fontname, Dimension.E(size))}