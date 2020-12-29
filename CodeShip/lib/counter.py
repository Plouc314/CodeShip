import time

class Counter:
    '''
    Static object, monitor performance of functions.  

    To keep track of the performance of a function,
    use `add_func` method, either as a decorator
    or by calling it.

    To get performance of a function, call `get_performance method`.  
    To get an overall view, call `print_result` method.  
    '''
    
    funcs = {
        'names': [],
        'iterations': [],
        'time': []
    }
    
    @classmethod
    def add_func(cls, func):
        '''
        Add a function to monitor performance.
        '''
        cls.funcs['names'].append(func.__qualname__)
        cls.funcs['iterations'].append(0)
        cls.funcs['time'].append(0)
        
        index = len(cls.funcs['names'])-1
        
        def inner(*args, **kwargs):
            cls.funcs['iterations'][index] += 1
            st = time.time()
            
            r = func(*args, **kwargs)
            
            cls.funcs['time'][index] += time.time() - st
            
            return r
        
        return inner
    
    @classmethod
    def print_result(cls):
        '''
        Print the performance of each function.
        '''
        print('Result:\n---')
        
        for i in range(len(cls.funcs['names'])):
            
            name = cls.funcs['names'][i]
            iteration = cls.funcs['iterations'][i]
            time = cls.funcs['time'][i]
            
            if iteration > 0:
                performance = time / iteration
            else:
                performance = 0
            
            print(name)
            print(f'    iterations: {iteration}   performance: {performance:.4f} sec   total: {time:.3f} sec')
            print('---')

    @classmethod
    def get_performance(cls, name):
        '''
        Return a dictionnary in the format: `{iterations, time, performance}`
        '''
        if not name in cls.funcs['names']:
            return
        
        idx = cls.funcs['names'].index(name)

        iterations = cls.funcs['iterations'][idx]
        time = cls.funcs['time'][idx]

        if iterations > 0:
            performance = time / iterations
        else:
            performance = 0

        return {'iterations':iterations, 'time':time, 'performance':performance}

    @classmethod
    def reset(cls):
        '''
        Reset values of every function.
        '''
        cls.funcs['time'] = [0 for _ in cls.funcs['names']]
        cls.funcs['iterations'] = [0 for _ in cls.funcs['names']]