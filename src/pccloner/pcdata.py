import time
from pynput import keyboard, mouse
import pyautogui
import os
import re
import keyboard as kb
import pandas as pd
import datetime

# Future work: 
#   Include PC sound, microphone, webcam
#   Make the same for smartphones
#   avoid adsminitrator permissions on ubuntu
#   The key identification for alt and other some keys will be changed from keyboard to keyboard 
#   Upload data https://ragug.medium.com/how-to-upload-files-using-the-google-drive-api-in-python-ebefdfd63eab

#   Make easy installation for windows users using pip install 

class Collector:
    def __init__(self, base_folder='data/'):
        self.mouse = mouse.Controller()
        self.counter = 0
        self.lastscreen = None
        self.data = []
        self.moves = []
        self.movelistener = mouse.Listener(on_move=self.on_move)
        self.movesflag = False
        self.base_folder = base_folder
        self.sample_folder = self.create_incremented_folder(self.base_folder) + '/' 
        
    # Monitoring
    def start(self):
        print("Waiting for activation with ESC key ...")
        kb.wait('esc')

        print("Monitoring is working ...")
        self.movelistener.start()  
        self.date = str(datetime.datetime.now()).split('.')[0].replace(':','-').replace(' ','_')
        self.running = True
        self.start_time = time.perf_counter()
        self.lastscreen = (time.perf_counter() - self.start_time, pyautogui.screenshot())
        with mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll), \
             keyboard.Listener(on_press=self.on_press, on_release=self.on_release):
            while self.running:
                self.lastscreen = (time.perf_counter() - self.start_time, pyautogui.screenshot())
        print("Monitoring was ended ...")

        data_df = pd.DataFrame(self.data, columns =['timestamp', 'img_path', 'px', 'py', 'event', 'trajectory'])
        data_df.to_csv(self.sample_folder + f'raw_pcdata_{self.date}.csv')
        self.movelistener.stop()

    # Mouse events
    def on_move(self, x, y):
        if self.movesflag == True:
            self.moves.append((time.perf_counter() - self.start_time, x, y)) 
        else:
            self.moves=[]

    def on_click(self, px, py, button, pressed):
        if pressed:
            self.movesflag = True
            self.savedata(px, py, event=f'pressed {button}')
        else:
            self.movesflag = False
            self.savedata(px, py, event=f'released {button}', trajectory=self.moves)

    def on_scroll(self, px, py, dx, dy):
        if dy == 1:
            scroll = 'pressed Scroll.down' 
        elif dy == -1:
            scroll = 'pressed Scroll.up'
        else:
            scroll = 'pressed Scroll.what?'
        self.savedata(px, py, event=scroll)
    
    # Keyboard events 
    def on_press(self, key):
        if key == keyboard.Key.esc: 
            self.running = False
        key = str(key).strip("'")
        px, py = self.mouse.position
        self.savedata(px, py, event=f'pressed {key}')
        
    def on_release(self, key):
        key = str(key).strip("'")
        px, py = self.mouse.position
        self.savedata(px, py, event=f'released {key}')

    def savedata(self, px, py, event, trajectory=[]):
        timestamp = time.perf_counter() - self.start_time
        t, img = self.lastscreen
        img_path = self.sample_folder + 'screen{:010}_{}.jpg'.format(self.counter, t)
        self.data.append((timestamp, img_path, px, py, event, trajectory))
        img.save(img_path)
        self.counter += 1

    # Initialize folder to save data
    def create_incremented_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        # Find the highest number
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        highest_num = 0
        for dir_name in dirs:
            match = re.match(r"sample(\d+)", dir_name)
            if match:
                highest_num = max(highest_num, int(match.group(1)))
        # Create new folder
        new_folder_name = f"sample{highest_num + 1}"
        new_folder_path = os.path.join(path, new_folder_name)
        os.makedirs(new_folder_path)
        return new_folder_path

    
