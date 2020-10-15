import pygame
import numpy as np
from lib.interface import Form, C
from spec import Spec


# load imgs
img_shield = pygame.image.load('imgs/shield.png')
img_shield = pygame.transform.scale(img_shield, Spec.DIM_ITEM)

img_energie = pygame.image.load('imgs/thunder.png')
img_energie = pygame.transform.scale(img_energie, Spec.DIM_ITEM)

img_turret = pygame.image.load('imgs/cannon.png')
img_turret = pygame.transform.rotate(img_turret, 90)
img_turret = pygame.transform.scale(img_turret, Spec.DIM_ITEM)

class Block(Form):

    def __init__(self, coord, color=None, image=None):

        self.coord = np.array(coord, dtype='int16')

        if color == None:
            color = C.BLUE
        # only set a font if the block has an image, else surf is a normal uni-color
        if image == None:
            with_font = False
        else:
            with_font = True

        # the position doesn't matter as the block's surface will be compiled in the ship image
        super().__init__(Spec.DIM_BLOCK, (0,0), color=color, surface=image, with_font=with_font, marge=True)

        self.set_marge_width(Spec.DIM_BLOCK_MARGE, scale=True)

    def display(self):
        super().display(marge=True)

class Energie(Block):

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        # blit the energie image on the surface -> can resize the image
        self.surf['original'].blit(img_energie, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surf(self.surf['original'])

class Shield(Block):

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        # blit the shield image on the surface -> can resize the image
        self.surf['original'].blit(img_shield, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surf(self.surf['original'])

class Turret(Block):

    def __init__(self, coord, color=None):
        super().__init__(coord, color=color)

        # blit the shield image on the surface -> can resize the image
        self.surf['original'].blit(img_turret, (Spec.DIM_BLOCK-Spec.DIM_ITEM)//2)
        self.set_surf(self.surf['original'])
