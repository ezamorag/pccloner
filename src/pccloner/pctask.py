import pyautogui
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# current limitations: 
# No drag actions, 
# Not pressed two keys o more at the same time
# pcontroller is prepared for all events

# Verify the current initial screen is compatable with the recorded initial screen. 
# Allow compounding tasks for big ones.   
class Replayer():
    def __init__(self, sample, data_dir):
        self.sample = sample
        self.data_dir = data_dir
 
    def preprocessing_actions(self): 
        actions = self.sample[self.sample['event'].map(lambda x: 'pressed' in x)].copy()
        actions['event'] = actions['event'].map(lambda x: x.replace('pressed ',''))
        delays = actions['timestamp'][1:].values - actions['timestamp'][0:-1].values
        delays = np.append(delays,0.0)
        actions['delay'] = delays
        actions = actions.reset_index(drop=True)
        self.actions = actions 

    def pcontroller(self, action, position, delay): 
        # Mouse
        if "Button." in action:
            if action == 'Button.left': 
                pyautogui.click(x=position[0], y=position[1])
            elif action == 'Button.right': 
                pyautogui.click(button='right', x=position[0], y=position[1])
        elif "scroll_" in action:
            if action == 'scroll_down': 
                pyautogui.scroll(-1, x=position[0], y=position[1])
            elif action == 'scroll_up': 
                pyautogui.scroll(1, x=position[0], y=position[1])
        # Keyboard
        elif "Key." in action: 
            if action == 'Key.enter':
                pyautogui.moveTo(position[0],position[1])
                pyautogui.press('enter')
            elif action == 'Key.esc':
                pyautogui.moveTo(position[0],position[1])
                pyautogui.press('esc')
        # Write with keyboard
        elif len(action) == 1 and action.isalpha():
            pyautogui.moveTo(position[0],position[1])
            pyautogui.write(action)
        else:
            print(f'This action {action} does not exist')
        time.sleep(delay)

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
    
    def execute(self, viz=False, screen_flag=True):
        self.preprocessing_actions()
        time.sleep(2)
        for index, action in self.actions.iterrows():
            if viz == True: 
                self.viz_actions(index, action, screen_flag)
            self.pcontroller(action['event'], (action['px'], action['py']), action['delay'])
        pyautogui.alert('The execution has been terminated.')