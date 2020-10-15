import numpy as np

class Spec:
    SIZE_BLOCK = 120
    DIM_BLOCK = np.array([120, 120], dtype='int16')
    DIM_ITEM = np.array([80, 80], dtype='int16')
    DIM_BLOCK_MARGE = 10
    SIZE_GRID_SHIP = 3
    SHAPE_GRID_SHIP = np.array([3,3], dtype='int16')
    DIM_SHIP = SHAPE_GRID_SHIP * DIM_BLOCK[0]