import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import pyautogui


# No double clicks (SOLVED)
# No drag actions (SOLVED) 
# pcontroller is prepared for all keyboard events (almost SOLVED)

# current limitations: 
# It has been tested only on Ubuntu 20.04.
# Not pressed two keys o more at the same time
# Verify the current initial screen is compatable with the recorded initial screen.  
# Allow compounding tasks for big ones.  
 
class Replayer():
    def __init__(self, sample, data_dir):
        self.sample = sample.copy()
        self.data_dir = data_dir
        self.processing = Preprocessing(length_th = 5, minpixels_th = 1, dt_th = 0.22, maxpixels_th = 0)
        self.pccontroller = pcController()
        
    def execute(self, viz=False, screen_flag=True):
        self.actions = self.processing.run(self.sample)
        time.sleep(2)
        for index, action in self.actions.iterrows():
            if viz == True: 
                self.viz_actions(index, action, screen_flag)
            self.pccontroller.run(action = action['event'], 
                                  position = (action['px'], action['py']), 
                                  endposition = (action['drag2px'], action['drag2py']), 
                                  #endposition = action['trajectory'], 
                                  delay = action['delay']) 
        pyautogui.alert('The execution has been terminated.')

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
        self.mouse_mapping = {
                'Button.left': lambda position, *args: self.clickleft(position),
                #'Button.left.double': lambda position, *args: pyautogui.doubleClick(x=position[0],y=position[1]),
                'Button.left.double': lambda position, *args: self.doubleclickleft(position),
                'Button.left.drag': lambda position, endposition: self.pyautogui_leftdrag(position, endposition), 
                #'Button.left.drag': lambda position, trajectory: self.leftdrag_following(position, trajectory),  
                'Button.right': lambda position, *args: self.clickright(position),
                'Scroll.down': lambda position, *args: self.scrolldown(position),
                'Scroll.up': lambda position, *args: self.scrollup(position),
            }
        self.none_mouse = lambda position, endposition: print("invalid mouse action")
        self.umapping = {
                '<269025048>': ['f4'], 
                '<269025062>': ['f6'],  
                '<65027>': ['alt_gr'], 
                '<65056>': ['shift_r', 'tab'],
                "['´']": [],   # tilde
                "['¨']": [],   # tilde con shift_r
                '"\'"': ["'"],   
            }

    def run(self, action, position, endposition, delay): 
        # Mouse
        if "Button." in action or "Scroll." in action:
            self.mouse_mapping.get(action, self.none_mouse)(position, endposition)
        # Writing
        elif len(action) == 1:
            self.push(action)
        # Known Keys
        elif "Key." in action:
            keyname = action.replace('Key.','')
            if keyname in Key.__dict__.keys():    
                button = Key.__dict__[keyname]
                self.push(button)
            else:
                print("invalid key action", action)
        # Unknown keys 
        elif action in self.umapping.keys():      
            key_sequence = self.umapping[action]
            if len(key_sequence) == 1: 
                if key_sequence[0] == "'":  
                    self.push("'")
                else: 
                    button = Key.__dict__[key_sequence[0]]
                    self.push(button)
            elif len(key_sequence) == 2: 
                button1 = Key.__dict__[key_sequence[0]]
                button2 = Key.__dict__[key_sequence[1]]
                with self.keyboard.pressed(button1):
                    self.push(button2)           
        else:
            print(f'The action {action} is not a key, not a mouse, not a char')
        time.sleep(delay)

    def push(self, button):
        self.keyboard.press(button)
        self.keyboard.release(button)

    def clickleft(self, position):
        self.mouse.position = position
        self.mouse.click(Button.left, 1)

    def doubleclickleft(self, position):
        self.mouse.position = position
        self.mouse.click(Button.left, 2)

    def pyautogui_leftdrag(self, position, endposition):
        self.mouse.position = position
        pyautogui.dragTo(endposition[0], endposition[1], 0.6, button='left')

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
        """ It's working but I'm not sure about its reliablity and it's slower """
        self.mouse.position = position
        self.mouse.press(Button.left)
        t0 = trajectory[0][0] - 0.2  # use the correct initial time
        for t,x,y in trajectory:
            time.sleep(t-t0 + 0.1)
            self.mouse.position = (x,y)
            t0 = t
        self.mouse.release(Button.left)


    def clickright(self, position):
        self.mouse.position = position
        self.mouse.click(Button.right, 1)

    def scrollup(self, position):
        self.mouse.position = position
        self.mouse.scroll(0, -1)

    def scrolldown(self, position):
        self.mouse.position = position
        self.mouse.scroll(0, 1)

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
        sample['trajectory'] = sample['trajectory'].map(lambda x: self.string2list(x))    # Convert a list represented as a string into a actual list
        sample = self.replace_drags(sample)                                               # Detect drag events
        actions = sample[sample['event'].map(lambda x: 'pressed' in x)].copy()            # Select pressed events only
        actions = self.replace_doubleclicks(actions)                                      # Detect double clicks
        actions['event'] = actions['event'].map(lambda x: x.replace('pressed ',''))       # Remove pressed string
        delays = actions['timestamp'][1:].values - actions['timestamp'][0:-1].values      # Calculating delays
        delays = np.append(delays,0.0)                                                
        actions['delay'] = delays
        actions = actions.reset_index(drop=True)                                          # Reset dataframe index
        return actions

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
        for ix in self.find_drags(sample):
            samplecopy.loc[ix, 'event'] = 'pressed Button.left.drag'
            samplecopy.loc[ix, 'drag2px'] = sample.loc[ix+1, 'px']
            samplecopy.loc[ix, 'drag2py'] = sample.loc[ix+1, 'py']
            samplecopy.at[ix, 'trajectory'] = sample.loc[ix+1, 'trajectory']
        return samplecopy
    
    def find_drags(self, sample):
        rBleft_indexes = sample.index[sample['event'].map(lambda x: 'released Button.left' in x)]
        drags_indexes = []
        for ix in rBleft_indexes:
            length = len(sample.loc[ix,'trajectory'])
            p1 = (sample.loc[ix-1,'px'],sample.loc[ix-1,'py'])
            p2 = (sample.loc[ix,'px'], sample.loc[ix,'py'])
            if (length >= self.length_th) and ((abs(p1[0]-p2[0]) >= self.minpixels_th) or (abs(p1[1] - p2[1]) >= self.minpixels_th)): 
                drags_indexes.append(ix-1)
        return drags_indexes
    
    def replace_doubleclicks(self, sample):
        """ Transform the dataframe to encode double events """
        samplecopy = sample.copy()
        for ix0,ix1 in self.find_doubleclicks(sample):
            samplecopy.loc[ix0, 'event'] = 'pressed Button.left.double'
            samplecopy = samplecopy.drop([ix1])
        return samplecopy

    def find_doubleclicks(self, sample):
        pBleft_indexes = sample.index[sample['event'].map(lambda x: 'pressed Button.left' in x)].tolist()
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