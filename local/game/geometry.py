import numpy as np

def get_rad(angle):
    return (angle * np.pi / 180) % (2 * np.pi)

def get_deg(angle):
    return (angle * 180 / np.pi) % 360

def get_polar(pos):
    r = np.sqrt(pos[0]**2 + pos[1]**2)
    alpha = np.arctan2(pos[1], pos[0])
    return r, alpha

def get_cartesian(r, alpha):
    x = r * np.cos(alpha)
    y = r * np.sin(alpha)
    return np.array([x,y])

def get_length(vect):
    return np.sqrt(vect[0]**2 + vect[1]**2)