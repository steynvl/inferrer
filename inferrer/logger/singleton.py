class Singleton:

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get('__it__')

        if it is not None:
            return it

        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwargs)
        return it

    def init(self, *args, **kwargs):
        pass
