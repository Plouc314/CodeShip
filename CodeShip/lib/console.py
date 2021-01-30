import re

class Console:

    @staticmethod
    def colored(string, color:str):
        colors = {
            'yellow': '\033[93m',
            'red': '\033[91m',
            'green': '\033[92m',
            'blue': '\033[94m',
            'normal': '\033[00m'
        }

        return colors[color] + string + colors['normal']

    @classmethod
    def print(cls, string: str, *args):
        '''
        Format & print a string to the terminal
        '''
        for arg in args:
            string += ' ' + str(arg)

        string = string.replace('[TCP]', cls.colored('[TCP]', 'yellow'))
        string = string.replace('[UDP]', cls.colored('[UDP]', 'yellow'))

        string = string.replace('[ERROR]', cls.colored('[ERROR]', 'red'))
        string = string.replace('[WARNING]', cls.colored('[WARNING]', 'red'))

        ids = re.findall('\{[a-z]+\}', string)

        if len(ids) > 0:
            string = string.replace(ids[0], cls.colored(ids[0], 'blue'))

        print(string)
