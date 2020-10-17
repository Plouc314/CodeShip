import numpy as np

class Spec:
    # block dimension
    SIZE_BLOCK = 100
    SIZE_TURRET = 80
    DIM_BLOCK = np.array([100, 100], dtype='int16')
    DIM_ITEM = np.array([70, 70], dtype='int16')
    DIM_TURRET = np.array([80, 80], dtype='int16')
    DIM_BULLET = np.array([20,20], dtype='int16')
    DIM_BLOCK_MARGE = 10
    
    # signal
    DIM_SIGNAL = np.array([20,20], dtype='int16')
    POS_SIGNAL = np.array([10,10], dtype='int16')

    # grid dimension
    SIZE_GRID_SHIP = 4
    SHAPE_GRID_SHIP = np.array([4,4], dtype='int16')
    DIM_SHIP = SHAPE_GRID_SHIP * DIM_BLOCK[0]

    # ship movement
    MAX_CIRCULAR_ACC = 0.00025 # rad
    MAX_CIRCULAR_SPEED = 0.05 # rad

    # block caracteristics
    HP_BLOCK = 100
    POWER_ENERGIE = 50
    POWER_CONS = 10
    POWER_CONS_MOTOR = 20
    MOTOR_POWER = 10
    TURRET_FIRE_DELAY = 20
    TURRET_MAX_SPEED = 2 # deg

    # bullet
    DAMAGE_BULLET = 10
    SPEED_BULLET = 40
    
    # explosion
    DIM_MAX_EXPL = np.array([60,60], dtype='int16')
    DIM_MIN_EXPL = np.array([20,20], dtype='int16')
    TIME_EXPL = 3 # frame