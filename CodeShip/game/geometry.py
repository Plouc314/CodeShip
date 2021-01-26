import numpy as np

def get_rad(angle) -> float:
    return (angle * np.pi / 180) % (2 * np.pi)

def get_deg(angle) -> float:
    return (angle * 180 / np.pi) % 360

def get_polar(pos) -> [float, float]:
    r = np.sqrt(pos[0]**2 + pos[1]**2)
    alpha = np.arctan2(pos[1], pos[0])
    return r, alpha

def get_cartesian(r, alpha) -> np.ndarray:
    x = r * np.cos(alpha)
    y = r * np.sin(alpha)
    return np.array([x,y])

def get_norm(vect) -> float:
    return np.sqrt(vect[0]**2 + vect[1]**2)

def to_vect(d, angle) -> np.ndarray:
    '''
    Return a `np.ndarray` of the vector resulting of the polar coordinate given.  
    `angle`: radian
    '''
    x = np.cos(angle) * d
    y = np.sin(angle) * d
    return np.array([x,y], dtype=float)

def cal_direction(a, b) -> float:
    '''
    Calculate the angle of the vector a to b
    '''
    return np.arctan2(b[1]-a[1], b[0]-a[0])
