from XPLMUtilities import *

from SandyBarbourUtilities import *

from settings import *


def log(msg='', value=None, xp_log=True, top_display=True):

    if not LOG_ENABLED:
        return

    if value is not None:
        log_msg = str(msg) + '=' + str(value) + '\n'
    else:
        log_msg = str(msg) + '\n'

    if xp_log:
        XPLMDebugString(log_msg)

    if top_display:
        SandyBarbourDisplay(log_msg)
