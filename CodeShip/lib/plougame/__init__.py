'''
Plougame
======

Plougame is an extension of the pygame module, 
it is written to create GUI while still using raw pygame beside.

The extension is organised in three layers of abstraction, 
which are, from the less abstract to the greater one:

1) Form-like objects: Object derived from `Form`

2) Page-like objects: Objects derived from `Page`

3) Application-like objects: Objects derived from `Application`
'''

# TODO:
# - generalize the nomenclature: scale/scaled
# - create .copy method for all components
# - Page: add frame func, in/out page func
# - Form: init marge value stored -> has marge when displayed
# - remove Cadre object

import pygame

pygame.init()

from .interface import Interface
from .form import Form
from .components import Cadre, TextBox, Button, InputText, ScrollList
from .auxiliary import Dimension, Font, C
from .spec import Specifications

from .page import Page, SubPage
from .app import Application