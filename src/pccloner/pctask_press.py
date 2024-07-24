import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import pyautogui
pyautogui.MINIMUM_DURATION = 0.01
pyautogui.FAILSAFE = False
from pynput import keyboard

# No double clicks (SOLVED)
# No drag actions (SOLVED) 
# pcontroller is prepared for all keyboard events (SOLVED form most common cases)
# It has been tested only on Ubuntu 20.04 and windows 11  (almost SOLVED)
# Not pressed two keys or more at the same time (SOLVED for most cases). No include mouse actions. 
# Hotkeys sequences: e1 + [(e7+e2) + e5 + (e7+e4)]    (SOLVED) 

# Future work:
# Known failures: 
#      1) SOMETIMES, I think that save one scroll.down more that it needs 
#      2) Sometimes, to minimize a window, change the size and location of the window (we do not have control about it)
# Mandatory: Test it on different keyboards and OS.
# Nice to have:
#    Add duration for drags action
#    Verify the current initial screen is compatable with the recorded initial screen.  
#    Allow compounding tasks for big ones.  


 
class Replayer():
    def __init__(self, sample, data_dir):
        self.sample = sample.copy()
        self.data_dir = data_dir
        self.processing = Preprocessing(length_th = 5, minpixels_th = 1, dt_th = 0.22, maxpixels_th = 0)
        self.pccontroller = pcController()
       
    def execute(self, viz, screen_flag, mousemoves_flag = False):
        self.running = True
        exitlistener = keyboard.Listener(on_press=self.on_press)
        self.actions = self.processing.run(self.sample)
        time.sleep(2)
        exitlistener.start()
        for index, action in self.actions.iterrows():
            if self.running == False:
                break
            if viz == True: 
                self.viz_actions(index, action, screen_flag)
            if mousemoves_flag == True:
                trajectory = action['trajectory']
            else:
                trajectory = []
            self.pccontroller.run(event = action['event'], 
                                  position = (action['px'], action['py']), 
                                  endposition = (action['drag2px'], action['drag2py']), 
                                  #endposition = action['trajectory'], 
                                  delay = action['delay'],
                                  trajectory = trajectory) 
        exitlistener.stop()
        pyautogui.alert('The execution has been terminated.')

    def on_press(self, key):
        if key == keyboard.Key.esc: 
            self.running = False

    def viz_actions(self, index, action, screen_flag):
        """ Tool for debugging actions """
        if index == 0:
            self.mfont = ImageFont.truetype("arial.ttf", 40)
            self.kfont = ImageFont.truetype("arial.ttf", 80)
            self.size = 10
            self.viz_dir = self.data_dir + 'viz/'
            Path(self.viz_dir).mkdir(parents=True, exist_ok=True)

        if screen_flag == True: 
            img = pyautogui.screenshot()
        else:
            img = Image.open(self.data_dir + action['img_path'])
        draw = ImageDraw.Draw(img)
        px = action['px']
        py = action['py']
        if 'Button.' in action['event']: 
            draw.ellipse([px-self.size/2,py-self.size/2,px+self.size//2,py+self.size//2], fill="red")
            draw.point((px,py), fill='yellow')
            draw.text((px,py), str(index), fill='red', font=self.mfont)
        else:
            draw.text((1920//2 - 100,1080//2), action['event'], fill='red', font=self.kfont)
        img.save(self.viz_dir + 'step{:04}.jpg'.format(index))


from pynput.keyboard import Key
from pynput.keyboard import Controller as kController
from pynput.mouse import Button 
from pynput.mouse import Controller as mController

class pcController(): 
    def __init__(self):
        self.mouse = mController()
        self.keyboard = kController()
        self.mousebuttons = ['Button.left','Button.right','Button.middle','Button.button8','Button.button9']
        self.mousespecials = {'Button.left.double': lambda position, *args: self.doubleclickleft(position),
                              'Button.left.drag': lambda position, endposition, *args: self.pyautogui_leftdrag(position, endposition), 
                              #'Button.left.drag': lambda position, trajectory: self.leftdrag_following(position, trajectory),  
                              }
        self.scrolls = {'Scroll.down':  lambda position, steps: self.scrolldown(position, steps),
                        'Scroll.up':    lambda position, steps: self.scrollup(position, steps),
                        'Scroll.left':  lambda position, steps: self.scrollleft(position, steps),
                        'Scroll.right': lambda position, steps: self.scrollright(position, steps),
                        }
        self.none_mouse = lambda position, endposition: print("invalid mouse action")

    def run(self, event, position, endposition, delay, trajectory): 
        if event != 'Button.left.drag' and trajectory != []:
            self.move_over_trajectory(position, trajectory)

        actions = event.split(' ')
        # Press
        for action in actions:
            if action in self.mousebuttons: 
                mbutton = action.replace('Button.','')
                if mbutton in Button.__dict__.keys():    
                    mbutton = Button.__dict__[mbutton]
                self.mouse.position = position
                self.mouse.press(mbutton)
            elif action in self.mousespecials.keys(): 
                self.mousespecials.get(event, self.none_mouse)(position, endposition)
            elif "Scroll." in action: 
                scrolltype, steps = action.split('_')
                self.scrolls.get(scrolltype, self.none_mouse)(position, int(steps))
            else: 
                key = self.classify_keystroke(action)
                self.keyboard.press(key)
        # Release
        for action in actions[::-1]:
            if action in self.mousebuttons: 
                mbutton = action.replace('Button.','')
                if mbutton in Button.__dict__.keys():    
                    mbutton = Button.__dict__[mbutton]
                self.mouse.position = position
                self.mouse.release(mbutton)
            elif action in self.mousespecials.keys() or "Scroll." in action: 
                pass
            else:
                key = self.classify_keystroke(action)
                self.keyboard.release(key)
        time.sleep(delay)

    def classify_keystroke(self, action):
        if len(action) == 1:   # Char
            key = action
        elif "Key." in action:
            keyname = action.replace('Key.','')
            if keyname in Key.__dict__.keys():    
                key = Key.__dict__[keyname]
            else:
                print("This Key is not in the dictionary of pynput", action) 
                key = None   
        else:
            print(f'The action {action} is unknown')
            key = None 
        return key
    
    def move_over_trajectory(self, position, trajectory, steps = 4):
        self.mouse.position = position
        for _, x, y in trajectory[::steps]: 
            pyautogui.moveTo(x,y)

    def doubleclickleft(self, position):
        self.mouse.position = position
        pyautogui.click(button='left', clicks=2, interval=0.25)

    def pyautogui_leftdrag(self, position, endposition):
        self.mouse.position = position
        pyautogui.dragTo(endposition[0], endposition[1], 2.0, button='left')  # Enough duration is important for reliability

    def leftdrag(self, position, endposition):
        """ this function is NOT reliable, use pyautogui_leftdrag instead """
        i = 35
        dposx = endposition[0]-position[0]
        dposy = endposition[1]-position[1]
        self.mouse.position = position
        self.mouse.press(Button.left)
        time.sleep(0.05)
        for di in range(1, i):
            self.mouse.position = ([position[0] + di*dposx//i, position[1] + di*dposy//i])
            time.sleep(0.05)
        self.mouse.release(Button.left)

    def leftdrag_following(self, position, trajectory):
        """ It's working but I'm not sure about its reliablity and it's slower, use pyautogui_leftdrag instead """
        self.mouse.position = position
        self.mouse.press(Button.left)
        t0 = trajectory[0][0] - 0.2  # use the correct initial time
        for t,x,y in trajectory:
            time.sleep(t-t0 + 0.1)
            self.mouse.position = (x,y)
            t0 = t
        self.mouse.release(Button.left)

    def scrollup(self, position, steps):
        self.mouse.position = position
        self.mouse.scroll(0, steps)

    def scrolldown(self, position, steps):
        self.mouse.position = position
        self.mouse.scroll(0, -steps)

    def scrollright(self, position, steps):
        self.mouse.position = position
        self.mouse.scroll(steps, 0)

    def scrollleft(self, position, steps):
        self.mouse.position = position
        self.mouse.scroll(-steps, 0)

# A simpler approach would be not to do this preprocessing and do replay including releases
# Avoiding hoykey, double clicks and drags detections 
class Preprocessing():
    def __init__(self, length_th, minpixels_th, dt_th, maxpixels_th): 
        # The thresholds for drag and doubleclicks detection determine the correct replay of task, how important are to calibrate them? 
        # Many of these functions make copies of dataframe, so it is not efficient. 
        # Drags
        self.length_th = length_th 
        self.minpixels_th = minpixels_th
        # Double clicks
        self.dt_th = dt_th 
        self.maxpixels_th = maxpixels_th

    def run(self, sample): 
        s1 = sample.copy()                                                          # The order of following processing is important
        s1['trajectory'] = s1['trajectory'].map(lambda x: self.string2list(x))      # Convert a list represented as a string into a actual list
        s1 = self.replace_drags(s1)                                                 # Detect drag events
        s1 = self.replace_doubleclicks(s1)                                          # Detect doubleclicks
        s1 = self.converts_shifted_events(s1)                                       # Convert shifted events which are different, but equivalent. 
        #s1.to_csv('shifted.csv')
        #check(s1)
        s1 = self.replace_hotkeys(s1)                                               # Detect hotkeys and combinations
        s1 = s1[s1['event'].map(lambda x: ('pressed' in x) or ('Scroll.' in x))].copy()   # Select pressed and scroll events
        s1['event'] = s1['event'].map(lambda x: x.replace('pressed ',''))                 # Remove pressed string
        delays = s1['timestamp'][1:].values - s1['timestamp'][0:-1].values                # Calculating delays
        delays = np.append(delays,0.0)                                                
        s1['delay'] = delays
        actions = s1.reset_index(drop=True)                                     # Reset dataframe index
        return actions
    
    def capsnumlocks_conversion(self, sample):
        """ This function is partially correct, don't use it"""
        # It requires to be prepared for especial cases where user keep press caps_locks while they are writing
        # I could n't understand the behavior of theses cases. 
        # I decided to not use it, until I solve this problem. 
        # The good thing is that for pctask_pr.py this function is not needed
        samplecopy = sample.copy()
        samplecopy = samplecopy.reset_index(drop=True)
        numlock_flag = False
        capslock_flag = False
        for i, event in enumerate(samplecopy['event']): 
            if event == 'pressed Key.caps_lock':
                capslock_flag = not capslock_flag 
            elif event == 'pressed Key.num_lock':
                numlock_flag = not numlock_flag
            elif '<65437>' in event: #Special case in Ubuntu only
                if numlock_flag: 
                    samplecopy.loc[i,'event'] = event.replace('<65437>', '5')
                else:
                    samplecopy.loc[i,'event'] = event.replace('<65437>', '')
            elif len(event.replace('pressed ','')) == 1 or len(event.replace('released ','')) == 1:
                if capslock_flag:
                    samplecopy.loc[i,'event'] = event[:-1] + event[-1].upper()
                else:
                    samplecopy.loc[i,'event'] = event[:-1] + event[-1].lower()
            else:
                pass
        return samplecopy 
    
    def converts_shifted_events(self, sample):
        """ Search for pressed and released events that are the same symbol because of shift key """
        # Find all Key.shift events -> Which key.shift event do have releases after it? -> 
        # -> Yes, does this release have a corresponding press event before shift? -> Yes, change the release event. 
        delta = 2  # 1 or 2, the other values have not been proven
        no_shifted = "|1234567890'¿qwertyuiop´+asdfghjklñ{}<zxcvbnm,.-"
        shifted =    '°!"#$%&/()=?¡QWERTYUIOP¨*ASDFGHJKLÑ[]>ZXCVBNM;:_'
        # Assuming this conversion is valid for all keyboards 
        def converts(c):
            co = None
            if c in no_shifted:
                co = shifted[no_shifted.index(c)]
            elif c in shifted:
                co = no_shifted[shifted.index(c)]
            else:
                print('This character was not found in shifted strings: {c}')
            return co
        
        samplecopy = sample.copy()
        samplecopy = samplecopy.reset_index(drop=True)
        ixs_shift = samplecopy.index[samplecopy['event'].map(lambda x: 'Key.shift_r' in x or 'Key.shift' in x or 'Key.shift_l' in x)].tolist()
        while len(ixs_shift) > 0:  # There must be at least 2 pressed events 
            ix = ixs_shift.pop(0)
            ix_releases = samplecopy.loc[ix+1:ix+1+delta].index[samplecopy.loc[ix+1:ix+1+delta,'event'].map(lambda x: 'released' in x)].tolist()
            for ixR in ix_releases:
                noshifted_key = samplecopy['event'][ixR].replace('released ', '')
                if len(noshifted_key) == 1: # This release event must be a single character
                    shifted_key = converts(noshifted_key)
                    possible_keys = samplecopy.loc[ix-delta:ix].index[samplecopy.loc[ix-delta:ix,'event'] == 'pressed ' + shifted_key].tolist()
                    r1 = samplecopy['event'][ix-delta].replace('pressed', 'released')
                    if len(possible_keys) > 0 and (samplecopy['event'][ix-delta+1] != r1): 
                        print(f'Correction for the shift event at {ixR}. ', samplecopy.loc[ixR,'event'], ' --> ' 'released ' + shifted_key)
                        samplecopy.loc[ixR,'event'] = 'released ' + shifted_key
                        
        return samplecopy 
       
    def replace_hotkeys(self, sample):
        """ Replace rows in the sample by hotkey events """
        # The key insight: consecutive pressed events form a hotkey. 
        # And the number of releases (di) between groups of consective pressed events determine the keys that are keeping press (basepressed). 
        # Note: Remove their corresponding releases
        samplecopy = sample.copy()
        samplecopy = samplecopy.reset_index(drop=True) 
        for ix, ixN in self.find_hotkeys(samplecopy):
            ixs_pressed = samplecopy.loc[ix:ixN].index[samplecopy.loc[ix:ixN,'event'].map(lambda x: 'pressed' in x)].tolist()
            pgroups = self.group_consecutive(ixs_pressed)  # Groups of consecutive position indexes of pressed events
            keep_ixs = []
            basepressed = []
            for i in range(len(pgroups)): 
                pgroup = basepressed + pgroups[i]
                newevent = 'pressed ' + samplecopy.loc[pgroup[0], 'event'].replace('pressed ', '')
                for ki in pgroup[1:]: 
                    newevent += ' ' + samplecopy.loc[ki, 'event'].replace('pressed ', '')
                samplecopy.loc[pgroup[-1], 'event'] = newevent
                keep_ixs.append(pgroup[-1])
                if i+1 < len(pgroups):
                    di = pgroups[i+1][0] - pgroup[-1] - 1
                    basepressed = pgroup[:-di]
            # Remove rows
            remove_ixs = [i for i in range(ix,ixN+1)]
            [remove_ixs.remove(i) for i in keep_ixs]
            samplecopy = samplecopy.drop(remove_ixs)
        return samplecopy 
    
    def group_consecutive(self, numbers):
        """ Making groups of consecutive numbers """ # numbers list cannot be empty by design.
        groups = []
        current_group = [numbers[0]]
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                current_group.append(numbers[i])
            else:
                groups.append(current_group)
                current_group = [numbers[i]]
        groups.append(current_group)
        return groups
    
    def find_hotkeys(self, sample):
        """ Look for candidates of hotkeys based on pressed events """
        ixs_pressed = sample.index[sample['event'].map(lambda x: 'pressed' in x)].tolist()
        hotkeys_indexes = []
        while len(ixs_pressed) >= 2:  # There must be at least 2 pressed events 
            ix = ixs_pressed[0]
            released1 = sample['event'][ix].replace('pressed', 'released')
            ixN = sample.loc[ix:].index[sample.loc[ix:,'event'] == released1][0]
            if ixN - ix >= 2 and not self.are_all_single_chars(ix, ixN, sample) and not self.are_all_thesamekey(ix, ixN, sample):  
                hotkeys_indexes.append((ix, ixN))
            for i in range(ix,ixN):
                try: 
                    ixs_pressed.remove(i)
                except:
                    pass
        return hotkeys_indexes
    
    def are_all_single_chars(self, ix, ixN, sample):
        """ Check if all pressed keys are characters """
        # Hotkeys must have at least a non-character key and not Key.space
        events = sample['event'][ix:ixN][sample['event'][ix:ixN].map(lambda x: 'pressed' in x)].tolist()
        #conds = [len(e.replace('pressed ','')) == 1 for e in events]
        conds = [(len(e.replace('pressed ','')) == 1) or (e.replace('pressed ','') == 'Key.space') for e in events]
        flag = conds[0]
        for c in conds[1:]:
            flag *= c
        return flag
    
    def are_all_thesamekey(self, ix, ixN, sample):
        """ Check if all pressed keys are the same key """
        # In this case, it is not hotkey, but a key continuously pressed
        events = sample['event'][ix:ixN][sample['event'][ix:ixN].map(lambda x: 'pressed' in x)].tolist()
        conds = [events[0] == e for e in events]
        flag = conds[0]
        for c in conds[1:]:
            flag *= c
        return flag

    def string2list(self, string): 
        """ Convert the trajectory string into an actual python list"""
        if isinstance(string, str):
            aux1 = string.strip('][').split('), (')
            if aux1[0] != '':
                aux2 = [x.strip(')(').split(', ') for x in aux1]
                trajectory = [(float(time), int(px), int(py)) for time,px,py in aux2]
            else:
                trajectory = []
        else:
            trajectory = []
        return trajectory

    def replace_drags(self, sample):
        """ Transform the dataframe to encode drag events"""
        samplecopy = sample.copy()
        samplecopy['drag2px'] = len(samplecopy)*[None]
        samplecopy['drag2py'] = len(samplecopy)*[None]
        for ix in self.find_drags(samplecopy):
            samplecopy.loc[ix, 'event'] = 'pressed Button.left.drag'
            samplecopy.loc[ix+1, 'event'] = 'released Button.left.drag'
            samplecopy.loc[ix, 'drag2px'] = samplecopy.loc[ix+1, 'px']
            samplecopy.loc[ix, 'drag2py'] = samplecopy.loc[ix+1, 'py']
            samplecopy.at[ix, 'trajectory'] = samplecopy.loc[ix+1, 'trajectory']
            samplecopy.at[ix+1, 'trajectory'] = []
        return samplecopy
    
    def find_drags(self, sample):
        rBleft_indexes = sample.index[sample['event'].map(lambda x: 'released Button.left' == x)]
        drags_indexes = []
        for ix in rBleft_indexes:
            if sample['event'][ix-1] == 'pressed Button.left':
                length = len(sample.loc[ix,'trajectory'])
                p1 = (sample.loc[ix-1,'px'],sample.loc[ix-1,'py'])
                p2 = (sample.loc[ix,'px'], sample.loc[ix,'py'])
                if (length >= self.length_th) and ((abs(p1[0]-p2[0]) >= self.minpixels_th) or (abs(p1[1] - p2[1]) >= self.minpixels_th)): 
                    drags_indexes.append(ix-1)
        return drags_indexes
    
    def replace_doubleclicks(self, sample):
        """ Transform the dataframe to encode double events """
        samplecopy = sample.copy()
        for ix0,ix1 in self.find_doubleclicks(samplecopy):
            samplecopy.loc[ix0, 'event'] = 'pressed Button.left.double'
            samplecopy.loc[ix1+1, 'event'] = 'released Button.left.double'
            samplecopy = samplecopy.drop([ix0+1, ix1])
        return samplecopy

    def find_doubleclicks(self, sample):
        pBleft_indexes = sample.index[sample['event'].map(lambda x: 'pressed Button.left' == x)].tolist()
        dclicks_indexes = []
        while len(pBleft_indexes) > 1:
            ix0, ix1 = pBleft_indexes[0], pBleft_indexes[1]
            dt = sample.loc[ix1, 'timestamp'] - sample.loc[ix0, 'timestamp']
            p1 = (sample.loc[ix0, 'px'], sample.loc[ix0, 'py'])
            p2 = (sample.loc[ix1, 'px'], sample.loc[ix1, 'py'])
            if (dt <= self.dt_th) and (abs(p1[0]-p2[0]) <= self.maxpixels_th) and (abs(p1[1] - p2[1]) <= self.maxpixels_th): 
                dclicks_indexes.append((ix0, ix1))
                pBleft_indexes.pop(1)   
            pBleft_indexes.pop(0)
        return dclicks_indexes