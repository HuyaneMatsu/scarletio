__all__ = ()

from ..utils import un_map_pack


KEY_KEYBOARD_INTERRUPT = '\x03'
KEY_DESTROY = '\x04'
KEY_TAB = '\x09'
KEY_NEW_LINE_ALL = ('\x0a', '\x0d')
KEY_ARROW_N_0 = '\x1b'
KEY_ARROW_N_1 = '\x5b'
KEY_ARROW_UP = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x41'
KEY_ARROW_DOWN = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x42'
KEY_ARROW_RIGHT = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x43'
KEY_ARROW_LEFT = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x44'
KEY_ARROW_END = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x46'
KEY_ARROW_HOME = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x48'
KEY_BACK_TAB = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x5a'
KEY_DELETE_RIGHT = KEY_ARROW_N_0 + KEY_ARROW_N_1 + '\x33' + '\x7e'
KEY_DELETE_LEFT = '\x7f'


KEY_NAMES = {
    KEY_KEYBOARD_INTERRUPT: 'keyboard interrupt',
    KEY_DESTROY: 'destroy',
    
    KEY_TAB: 'tab',
    KEY_BACK_TAB: 'back tab',
    
    **un_map_pack(((character, 'new line') for character in KEY_NEW_LINE_ALL)),
    
    KEY_ARROW_UP: 'arrow up',
    KEY_ARROW_DOWN: 'arrow down',
    KEY_ARROW_RIGHT: 'arrow right',
    KEY_ARROW_LEFT: 'arrow left',
    
    KEY_ARROW_END: 'end',
    KEY_ARROW_HOME: 'home',
    
    KEY_DELETE_RIGHT: 'delete',
    KEY_DELETE_LEFT: 'backspace',
}
