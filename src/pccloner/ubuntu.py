mapping = {
'<269025048>': 'Key.f4', 
'<269025062>': 'Key.f6', 
'<269025049>': 'email button',
'<269025053>': 'calculator_button', 
'<65027>': 'Key.alt_gr', 
'<65056>': 'Key.tab',   # when shift+tap
#'<65437>': '5' or None, # button 5 in calculator keyboard (5 if num_lock is not set, nothing if set)
"['´']": "´", # "['´']": '´',  # tilde   
"['¨']": "¨", # "['¨']": '¨',  # tilde con shift_r
'"\'"': "'",   
}


import subprocess

def check_locks(): 
    # Caution: "There are cases where the keyboard LED does not accurately represent the state of caps lock"
    # https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status

    # Ensure your operating system and keyboard drivers are up to date.
    # Check for any hardware issues with the keyboard.
    # Be aware of software that might independently control keyboard LEDs and cause discrepancies.
    # Use diagnostic tools or utilities provided by the keyboard manufacturer to check the LED functionality.
    x = subprocess.check_output('xset q | grep LED', shell=True)[65]
    if x==48 or x==50:  #caps off
        stop=False
        if x == 50:  #num on
            print("Please turn off NUM_LOCK before continue!")
            stop = True
    elif x==49 or x==51:  #caps on
        print("Please turn off CAPS_LOCK before continue!")
        stop = True
        if x == 51:  #num on
            print("Please turn off NUM_LOCK before continue!")
            stop = True
    return stop

