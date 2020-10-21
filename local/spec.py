import numpy as np

class Spec:

    ### comm ###

    PORT = 5050
    IP_PUBLIC = '188.62.158.181'
    IP_HOST = '127.0.0.1'
    ADDR_HOST = (IP_HOST, PORT)
    ADDR_PUBLIC = (IP_PUBLIC, PORT)
    
    SEP_MAIN = '|'
    SEP_CONTENT = ','

    ### game ###

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


    ### ui ###

    CENTER_X = 1600
    CENTER_Y = 800

    POS_TITLE = np.array([1400, 100], dtype='int16')
    DIM_TITLE = np.array([400,100], dtype='int16')

    DIM_MEDIUM_TEXT = np.array([400,60], dtype='int16')
    DIM_BIG_BUTTON = np.array([320,80], dtype='int16')
    DIM_MEDIUM_BUTTON = np.array([240,60], dtype='int16')

    