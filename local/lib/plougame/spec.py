
class Specifications:
    FPS = 30
    TEXT_DELAY = FPS // 10
    CURSOR_DELAY = FPS // 2

    @classmethod
    def set_fps(cls, fps):
        '''Set the number of FPS'''
        cls.FPS = fps
        cls.TEXT_DELAY = fps // 10
        cls.CURSOR_DELAY = fps // 10