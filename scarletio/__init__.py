__version__ = '1.0.96'


from .core import *
from .dns_query import *
from .ext import *
from .utils import *


__all__ = (
    *core.__all__,
    *dns_query.__all__,
    *ext.__all__,
    *utils.__all__,
)


from .utils.export_include import check_satisfaction
check_satisfaction()

AnsiTextDecoration = ANSITextDecoration
