
class Specifications:
    
    # time
    FPS = 30
    TEXT_DELAY = FPS // 10
    CURSOR_DELAY = FPS // 2

    MARGE_WIDTH = 4
    MARGE_TEXT = 5
    WIDTH_SCROLL_BAR = 10

    @classmethod
    def set_fps(cls, fps):
        '''Set the number of FPS'''
        cls.FPS = fps
        cls.TEXT_DELAY = fps // 10
        cls.CURSOR_DELAY = fps // 10