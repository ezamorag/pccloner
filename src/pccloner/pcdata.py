import time
from pynput import keyboard, mouse
import pyautogui
import os
import re
import pandas as pd
import datetime
from . import win11, ubuntu

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
        self.scrolls = {-1: 'Scroll.down', 1:'Scroll.up'}
        self.sample_folder = self.create_incremented_folder(self.base_folder) + '/' 

        if keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._win32':
            self.mapping = win11.mapping
            self.on_press = self.on_press_win11
            self.on_release = self.on_release_win11
            self.blockedkeys = [keyboard.Key.__dict__[kname] for kname in win11.blockedknames]
            self.previouskey = 0
        elif keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._xorg':
            self.mapping = ubuntu.mapping
            self.on_press = self.on_press_ubuntu
            self.on_release = self.on_release_ubuntu

    # Monitoring
    def start(self):
        print("Waiting for activation with ESC key ...")
        with keyboard.Listener(on_press=self.wait_esc) as wait:
            wait.join()

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
        data_df.to_csv(self.sample_folder + f'raw_pcdata_{self.date}.csv', index=False)
        self.movelistener.stop()

        return data_df

    # Mouse events
    def on_move(self, x, y):
        self.moves.append((time.perf_counter() - self.start_time, x, y)) 

    def on_click(self, px, py, button, pressed):
        if pressed:
            self.savedata(px, py, event=f'pressed {button}', trajectory=self.moves)
        else:
            self.savedata(px, py, event=f'released {button}', trajectory=self.moves)

    def on_scroll(self, px, py, dx, dy):
        try:
            self.savedata(px, py, event=self.scrolls[dy], trajectory=self.moves)
        except:
            print(dy, type(dy))
    
    #### Keyboard events 
            
    # Ubuntu
    def on_press_ubuntu(self, key):
        if key != keyboard.Key.esc: 
            key = self.mapping.get(str(key), key)
            keystring = str(key).strip("'") if str(key) != "'" else str(key)
            px, py = self.mouse.position
            self.savedata(px, py, event=f'pressed {keystring}', trajectory=self.moves)
        else: 
            self.running = False
            
    def on_release_ubuntu(self, key):
        if key != keyboard.Key.esc: 
            key = self.mapping.get(str(key), key)
            keystring = str(key).strip("'") if str(key) != "'" else str(key)
            px, py = self.mouse.position
            self.savedata(px, py, event=f'released {keystring}', trajectory=self.moves)

    # Windows11
    def on_press_win11(self, key):
        if key != keyboard.Key.esc: 
            if not ((key in self.blockedkeys) and (key == self.previouskey)):
                key = self.mapping.get(str(key), key)
                keystring = str(key).strip("'") if str(key) != "'" else str(key)
                px, py = self.mouse.position
                self.savedata(px, py, event=f'pressed {keystring}', trajectory=self.moves)
        else: 
            self.running = False
        self.previouskey = key

    def on_release_win11(self, key):
        if key != keyboard.Key.esc: 
            if key == self.previouskey:
                self.previouskey = 0
            key = self.mapping.get(str(key), key)
            keystring = str(key).strip("'") if str(key) != "'" else str(key)
            px, py = self.mouse.position
            self.savedata(px, py, event=f'released {keystring}', trajectory=self.moves)


    def savedata(self, px, py, event, trajectory=[]):
        timestamp = time.perf_counter() - self.start_time
        t, img = self.lastscreen
        img_path = self.sample_folder + 'screen{:010}_{}.jpg'.format(self.counter, t)
        self.data.append((timestamp, img_path, px, py, event, trajectory))
        img.save(img_path)
        self.counter += 1
        self.moves = []

    def wait_esc(self, key):
        if key != keyboard.Key.esc: 
            return True
        return False

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

    
