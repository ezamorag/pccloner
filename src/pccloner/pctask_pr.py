import time, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import pyautogui
pyautogui.MINIMUM_DURATION = 0.01
pyautogui.FAILSAFE = False
from pynput import keyboard
from . import win11, ubuntu



# Future work:
# Known failures: 
#      1) SOMETIMES, I think that save one scroll.down more that it needs 
#      2) Sometimes, to minimize a window, change the size and location of the window (we do not have control about it)
# Mandatory: Test it on different keyboards and OS.
# Nice to have:
#    Add duration for drags action
#    Verify the current initial screen is compatitable with the recorded initial screen.  
#    Allow compounding tasks for big ones.  
 
class Replayer():
    def __init__(self, sample, data_dir):
        self.sample = sample.copy()
        self.data_dir = data_dir
        self.processing = Preprocessing(length_th = 5, minpixels_th = 1, dt_th = 0.22, maxpixels_th = 0)
        self.pccontroller = pcController()
       
    def execute(self, viz, screen_flag, mousemoves_flag):
        self.locks_checking()
        self.pccontroller.mousemoves_flag = mousemoves_flag
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
            self.pccontroller.run(event = action['event'], 
                                  position = (action['px'], action['py']),  
                                  delay = action['delay'],
                                  trajectory = action['trajectory']) 
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

    def locks_checking(self): 
        if keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._win32':
            locks = win11.LockStates()
            locks.reset_all()
        elif keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._xorg':
            while ubuntu.check_locks(): # Stop execution until caps and num locks are off
                time.sleep(2)
                os.system('clear')

from pynput.keyboard import Key
from pynput.keyboard import Controller as kController
from pynput.mouse import Button 
from pynput.mouse import Controller as mController

class pcController(): 
    def __init__(self):
        self.mousemoves_flag = True
        self.mouse = mController()
        self.keyboard = kController()
        self.mousebuttons = ['Button.left','Button.right','Button.middle','Button.button8','Button.button9']
        self.scrolls = {'Scroll.down':  lambda position, steps: self.scrolldown(position, steps),
                        'Scroll.up':    lambda position, steps: self.scrollup(position, steps),
                        'Scroll.left':  lambda position, steps: self.scrollleft(position, steps),
                        'Scroll.right': lambda position, steps: self.scrollright(position, steps),
                        }

    def run(self, event, position, delay, trajectory): 
        if event != 'Button.left.drag' and trajectory != [] and self.mousemoves_flag:
            self.move_over_trajectory(trajectory)

        if 'pressed ' in event: 
            action = event.replace('pressed ', '')
            if action in self.mousebuttons: 
                mbutton = action.replace('Button.','')
                if mbutton in Button.__dict__.keys():    
                    mbutton = Button.__dict__[mbutton]
                self.mouse.position = position
                self.mouse.press(mbutton)
            else: 
                key = self.classify_keystroke(action)
                try:
                    self.keyboard.press(key)
                except:
                    print(f"The key {key} wasn't pressed")
        elif 'released ' in event: 
            action = event.replace('released ', '')
            if action in self.mousebuttons: 
                mbutton = action.replace('Button.','')
                if mbutton in Button.__dict__.keys():    
                    mbutton = Button.__dict__[mbutton]
                self.mouse.position = position
                self.mouse.release(mbutton)
            else:
                key = self.classify_keystroke(action)
                try:
                    self.keyboard.release(key)
                except:
                    print(f"The key {key} wasn't released")
        elif 'Scroll.' in event: 
            scrolltype, steps = event.split('_')
            self.scrolls.get(scrolltype)(position, int(steps))
        elif event == 'Button.left.double': 
            self.doubleclickleft(position)
        elif event == 'Button.left.drag':
            self.pyautogui_leftdrag(position, trajectory)
        else:
            print(f'Warning: this event was not in the official set of events: {event, position}')
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
            key = action 
        return key
    
    def move_over_trajectory(self, trajectory, steps = 4):
        for _, x, y in trajectory[::steps]: 
            pyautogui.moveTo(x,y)

    def doubleclickleft(self, position):
        self.mouse.position = position
        pyautogui.click(button='left', clicks=2, interval=0.25)

    def pyautogui_leftdrag(self, position, trajectory):
        self.mouse.position = position
        endposition = trajectory[-1][1:]
        pyautogui.dragTo(endposition[0], endposition[1], 2.0, button='left')  # Enough duration is important for reliability

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
        #s1 = self.capsnumlocks_conversion(s1)                                       # Conversion according with num_lock and caps_lock states
        s1 = self.replace_drags(s1)                                                 # Detect drag events
        s1 = self.replace_doubleclicks(s1)                                          # Detect doubleclicks
        delays = s1['timestamp'][1:].values - s1['timestamp'][0:-1].values          # Calculating delays
        delays = np.append(delays,0.0)                                                
        s1['delay'] = delays
        actions = s1.reset_index(drop=True)                                     # Reset dataframe index
        return actions 
    
    def capsnumlocks_conversion(self, sample):
        """ This function is partially correct, don't use it"""
        # It requires to be prepared for especial cases where user keeps press caps_locks while they are writing
        # I couldn't understand the behavior of theses cases. I decided to not use it, until I solve this problem. 
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
        samplecopy = samplecopy.reset_index(drop=True) 
        drags_indexes = self.find_drags(samplecopy)
        for ix in drags_indexes:
            samplecopy.loc[ix+1, 'px'] = samplecopy['px'][ix]
            samplecopy.loc[ix+1, 'py'] = samplecopy['py'][ix]
            samplecopy.loc[ix+1, 'event'] = 'Button.left.drag'
        samplecopy = samplecopy.drop(drags_indexes)
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
        samplecopy = samplecopy.reset_index(drop=True) 
        for ix0,ix1 in self.find_doubleclicks(samplecopy):
            samplecopy.loc[ix0, 'event'] = 'Button.left.double'
            samplecopy.loc[ix0, 'timestamp'] = samplecopy['timestamp'][ix1+1]
            samplecopy = samplecopy.drop([ix0+1, ix1, ix1+1])
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