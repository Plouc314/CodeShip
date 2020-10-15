import numpy as np

class Spec:
    # block dimension
    SIZE_BLOCK = 100
    DIM_BLOCK = np.array([100, 100], dtype='int16')
    DIM_ITEM = np.array([70, 70], dtype='int16')
    DIM_TURRET = np.array([80, 80], dtype='int16')
    DIM_BLOCK_MARGE = 10
    
    # grid dimension
    SIZE_GRID_SHIP = 4
    SHAPE_GRID_SHIP = np.array([4,4], dtype='int16')
    DIM_SHIP = SHAPE_GRID_SHIP * DIM_BLOCK[0]

    # ship movement
    MAX_CIRCULAR_ACC = 0.00025
    MAX_CIRCULAR_SPEED = 0.05

    # block caracteristics
    HP_BLOCK = 100
    DAMAGE_TURRET = 10
    POWER_ENERGIE = 50
    POWER_CONS = 10
    POWER_CONS_MOTOR = 20
    MOTOR_POWER = 10