import os, sys
import pygame

if sys.platform.startswith('darwin'):
    # build pygame font cache
    print("Building Pygame font's cache (might take a little while)...")
    pygame.font.init()
    pygame.font.get_default_font()


# clean up setup files
if os.path.exists('requirements.txt'):
    os.remove('requirements.txt')

if os.path.exists('setup.py'):
    os.remove('setup.py')

