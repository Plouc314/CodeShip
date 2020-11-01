'''
Plougame

-------

Plougame is an extension of the pygame module, it is written to create GUI while still using raw pygame beside.
The main features are: static object Interface, Form, TextBox, Button, InputText & Cadre
'''

import pygame

pygame.init()

from .interface import Interface
from .form import Form
from .components import Cadre, TextBox, Button, InputText, ScrollList
from .aux import Dimension, Font, C
from .spec import Specifications

from .page import Page, SubPage
from .app import Application