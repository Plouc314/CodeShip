import numpy as np
from lib.plougame.aux import C

class Spec:

    ### comm ###

    PORT = 5050
    IP_PUBLIC = '188.62.158.181'
    IP_HOST1 = '127.0.0.1'
    IP_HOST2 = '192.168.1.122'
    
    SEP_MAIN = '|'
    SEP_CONTENT = ','
    SEP_CONTENT2 = '*'

    ### game ###

    # block dimension
    SIZE_BLOCK = 100
    SIZE_TURRET = 80
    DIM_BLOCK = np.array([100, 100])
    DIM_ITEM = np.array([70, 70])
    DIM_TURRET = np.array([80, 80])
    DIM_BULLET = np.array([20,20])
    DIM_BLOCK_MARGE = 10
    
    # signal
    DIM_SIGNAL = np.array([20,20])
    POS_SIGNAL = np.array([10,10])

    # grid dimension
    SIZE_GRID_SHIP = 6
    SHAPE_GRID_SHIP = np.array([6,6])
    DIM_SHIP = SHAPE_GRID_SHIP * DIM_BLOCK[0]

    # ship config
    CREDITS_TOTAL = 1000
    PRICE_BLOCK = 40
    PRICE_ENGINE = 70
    PRICE_GENERATOR = 70
    PRICE_SHIELD = 60
    PRICE_TURRET = 90

    # ship movement
    MAX_CIRCULAR_ACC = 0.00025 # rad
    MAX_CIRCULAR_SPEED = 0.05 # rad

    # block caracteristics
    HP_BLOCK = 100
    POWER_ENERGIE = 50
    POWER_CONS = 10
    POWER_CONS_MOTOR = 20
    MOTOR_POWER = 10
    TURRET_FIRE_DELAY = 2
    TURRET_MAX_SPEED = 2 # deg

    # bullet
    DAMAGE_BULLET = 20
    SPEED_BULLET = 40
    HIT_DURATION = 5

    # explosion
    DIM_MAX_EXPL = np.array([60,60])
    DIM_MIN_EXPL = np.array([20,20])
    TIME_EXPL = 3 # frame

    # game
    OWN_TEAM = 1
    OPP_TEAM = 2
    COLOR_P1 = C.BLUE
    COLOR_P2 = C.PURPLE
    LCOLOR_P1 = C.LIGHT_BLUE
    LCOLOR_P2 = C.LIGHT_PURPLE
    POS_P1 = np.array([400, 500])
    POS_P2 = np.array([2200, 500])

    ### ui ###

    CENTER_X = 1600
    CENTER_Y = 800

    POS_TITLE = np.array([1400, 100])
    DIM_TITLE = np.array([400,100])

    DIM_BIG_TEXT = np.array([400,80])
    DIM_MEDIUM_TEXT = np.array([400,60])
    DIM_SMALL_TEXT = np.array([400,40])

    DIM_BIG_BUTTON = np.array([320,80])
    DIM_MEDIUM_BUTTON = np.array([240,60])
    DIM_SMALL_BUTTON = np.array([200,40])

    DIM_CHAT = np.array([1000,600])
    DIM_NOTIF = np.array([30,30])

    DIM_ICON = np.array([40,40])

    # page names
    PAGE_MENU = "menu"
    PAGE_CONN = "conn"
    PAGE_FRIENDS = "friends"
    PAGE_SHIP = "ship"

    CHAT_MAX_MSG = 20