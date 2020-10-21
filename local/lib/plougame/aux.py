import pygame

class Dimension:
    f = 1

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
        cls.x = dim[0]
        cls.y = dim[1]

    @classmethod
    def get_window_dim(cls):
        '''Return the scaled dimension of the window'''
        return cls.scale(cls.WINDOW)

    @classmethod
    def scale(cls, x, factor=None, fp=None):
        
        if factor:
            f = factor
        else:
            f = cls.f

        if type(x) == list or type(x) == tuple:
            x = list(x)
            for i in range(len(x)):
                x[i] = round(x[i]*f, fp)
        else:
            x = round(x*f, fp)
        return x

    @classmethod
    def inv_scale(cls, x, fp=5):
        '''
        Inverse the scale of the number: scale -> unscale ( note: unscale -> ?!@#@ )

        Arguments:
            - fp : floating point of the unscaled number (to keep precision)

        '''
        f = 1/cls.f
        if type(x) == list or type(x) == tuple:
            x = list(x)
            for i in range(len(x)):
                x[i] = round(x[i]*f, fp)
        else:
            x = round(x*f, fp)
        return x

    @classmethod
    def E(cls, x, *, fp=None):
        return round(x*cls.f, fp)

class C:
    '''Container of predefined colors'''
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    LIGHT_BLUE = (135,206,250)
    BLUE = (65,105,225)
    DARK_BLUE = (7, 19, 134)
    LIGHT_GREY = (200,200,200)
    XLIGHT_GREY = (230,230,230)
    LIGHT_RED = (255, 80, 80)
    RED = (225, 50, 50)
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