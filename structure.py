class Singleton(object):
    """Decorator class to make singleton structure"""
    def __init__(self, decorated):
        self._target = decorated

    def instance(self):
        if hasattr(self, '_instance'):
            return self._instance
        else:
            self._instance = self._target()
            return self._instance
        

    def __call__(self):
        raise TypeError('Singletons must be created using Instance() ')

    def __instancecheck__(self,inst):
        return isinstance(inst, self._target)