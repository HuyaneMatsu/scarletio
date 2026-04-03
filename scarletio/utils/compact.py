__all__ = ()

# Test for pypy bug:
# https://foss.heptapod.net/pypy/pypy/issues/3239
class dummy_init_tester:
    def __new__(cls, value):
        return object.__new__(cls)
    __init__ = object.__init__

try:
    dummy_init_tester(None)
except TypeError:
    NEEDS_DUMMY_INIT = True
else:
    NEEDS_DUMMY_INIT = False

del dummy_init_tester
