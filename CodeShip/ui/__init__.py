from data.spec import Spec
import os

# load templates
Spec.formatter.process_templates(os.path.join('ui','data','template.json'))

from .connection import Connection
from .menu import Menu
from .friends import Friends
from .editor import Editor
from .profil import Profil
from .updater import Updater
from .offline import Offline
from .chat import Chat
from .script_analyser import ScriptAnalyser
from .ship_editor import ShipEditor
from .doc import Doc