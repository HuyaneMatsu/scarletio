__all__ = ('LOOP_TIME', 'LOOP_TIME_RESOLUTION')

import time as module_time


LOOP_TIME = module_time.monotonic
LOOP_TIME_RESOLUTION = module_time.get_clock_info('monotonic').resolution
