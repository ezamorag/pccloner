mapping = {
'Button.x1': 'Button.button8',  # Backwards
'Button.x2': 'Button.button9',  # Forwards
"['´']": "´", # "['´']": '´',  # tilde   
"['¨']": "¨", # "['¨']": '¨',  # tilde con shift_r

# Calculator in keyboard (without num_lock)
'<96>': '0',
'<97>': '1',
'<98>': '2',
'<99>': '3',
'<100>': '4',
'<101>': '5',
'<102>': '6',
'<103>': '7',
'<104>': '8',
'<105>': '9',
'<110>': '.',

# Without num_lock
#'<12>': Nothing happens, press 5 in calculator keyboard. 

# with altgr
'<49>': '1',
'<50>': '2',
'<51>': '3',
'<52>': '4',
'<53>': '5',
'<54>': '6',
'<55>': '7',
'<56>': '8',
'<57>': '9',
'<48>': '0',
'<221>': '¿',

'<87>': 'w',
'<69>': 'e',
'<82>': 'r',
'<84>': 't',
'<89>': 'y',
'<85>': 'u',
'<73>': 'i',
'<79>': 'o',
'<80>': 'p',
'<186>': '´', # '´',
'<187>': '+',

'<65>': 'a',
'<83>': 's',
'<68>': 'd',
'<70>': 'f', 
'<71>': 'g',
'<72>': 'h',
'<74>': 'j',
'<75>': 'k',
'<76>': 'l',
'<192>': 'ñ',

'<90>': 'z',
'<88>': 'x',
'<67>': 'c',
'<86>': 'v',
'<66>': 'b',
'<78>': 'n',
'<77>': 'm',
'<188>': ',',
'<190>': '.',
'<189>': '-',
'<225>': 'Key.fn',
'<226>': '<',

# with ctrl
'<220>': '|',
"'\\x1c'": "'",

"'\\x11'": 'q',
"'\\x17'": 'w',
"'\\x05'": 'e',
"'\\x12'": 'r',
"'\\x14'": 't',
"'\\x19'": 'y',
"'\\x15'": 'u',
"'\\t'": 'i',
"'\\x0f'": 'o',
"'\\x10'": 'p',
"'\\x1d'": '}',

"'\\x01'": 'a',
"'\\x13'": 's',
"'\\x04'": 'd',
"'\\x06'": 'f', 
"'\\x07'": 'g',
"'\\x08'": 'h',
"'\\n'": 'j',
"'\\x0b'": 'k',
"'\\x0c'": 'l',
"'\\x1b'": '{',

"'\\x1a'": 'z',
"'\\x18'": 'x',
"'\\x03'": 'c',
"'\\x16'": 'v',
"'\\x02'": 'b',
"'\\x0e'": 'n',
"'\\r'": 'm',
"'\\x1f'": '-',

"'\\x1c'": '<',

}

blockedknames = ['ctrl', 'ctrl_l', 'ctrl_r', 
                 'alt', 'alt_l', 'alt_r', 'alt_gr',
                 'shift', 'shift_r', 'shift_l']


import ctypes

class LockStates: 
    def __init__(self): 
        self.VK_CAPITAL = 0x14  # Change to Caps Lock key code
        self.VK_NUMLOCK = 0x90
        self.VK_SCROLL = 0x91
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)

    def reset_all(self):
        # Get the current Caps Lock state
        is_caps_lock_on = self.get_capslock_state(self.VK_CAPITAL)
        if is_caps_lock_on:
            print('The caps_lock was on, we turn it off for you')
            self.toggle_capslock(self.VK_CAPITAL)

        is_numlock_on = self.get_numlock_state(self.VK_NUMLOCK)
        if is_numlock_on:
            print('The num_lock was on, we turn it off for you')
            self.toggle_numlock(self.VK_NUMLOCK)

        is_scroll_lock_on = self.get_scrlock_state(self.VK_SCROLL)
        if is_scroll_lock_on:
            print('The scroll_lock was on, we turn it off for you')
            self.toggle_scrlock(self.VK_SCROLL)

    def get_capslock_state(self, vk):
        return bool(self.user32.GetKeyState(vk) & 0x0001)

    def toggle_capslock(self, vk):
        self.user32.keybd_event(vk, 0x45, 0, 0)  # Key down
        self.user32.keybd_event(vk, 0x45, 0x0002, 0)  # Key up

    def get_numlock_state(self, vk):
        return bool(self.user32.GetKeyState(vk) & 0x0001)

    def toggle_numlock(self, vk):
        self.user32.keybd_event(vk, 0x45, 0, 0)  # Key down
        self.user32.keybd_event(vk, 0x45, 0x0002, 0)  # Key up

    def get_scrlock_state(self, vk):
        return bool(self.user32.GetKeyState(vk) & 0x0001)

    def toggle_scrlock(self, vk):
        self.user32.keybd_event(vk, 0x45, 0, 0)  # Key down
        self.user32.keybd_event(vk, 0x45, 0x0002, 0)  # Key up


import locale

def get_keyboard_language():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    klid = user32.GetKeyboardLayout(0)
    lang_id = klid & 0xFFFF
    language_code = locale.windows_locale[lang_id]
    return language_code

