import time, os, math, locale, subprocess, json, logging
from pynput import keyboard, mouse
import pyautogui
import re
import pandas as pd
import datetime
from . import win11, ubuntu
import platform
import shutil

# Future work: 
#   Include PC sound, microphone, webcam
#   Make the same for smartphones
#   avoid adsminitrator permissions on ubuntu
#   The key identification for alt and other some keys will be changed from keyboard to keyboard 
#   Upload data https://ragug.medium.com/how-to-upload-files-using-the-google-drive-api-in-python-ebefdfd63eab

#   Make easy installation for windows users using pip install 

class Collector:
    def __init__(self, base_folder='data/', print_events = False):
        self.print_events = print_events
        self.mouse = mouse.Controller()
        self.counter = 0
        self.lastscreen = None
        self.data = []
        self.moves = []
        self.movelistener = mouse.Listener(on_move=self.on_move)
        self.movesflag = False
        self.base_folder = base_folder
        self.vscrolls = {-1: 'Scroll.down', 1:'Scroll.up'}
        self.hscrolls = {-1: 'Scroll.left', 1:'Scroll.right'}
        self.sample_folder = self.create_incremented_folder(self.base_folder) + '/' 
        self.logger = self.creating_logger()
        initial_df = pd.DataFrame({}, columns =['timestamp', 'img_path', 'px', 'py', 'event', 'trajectory']) 
        initial_df.to_csv(self.sample_folder + 'rawpcdata_temp.csv', index=False)

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
        self.locks_checking()
        print("Great! Monitoring has started! ")
        self.savemetada()
        self.movelistener.start()  

        self.running = True
        self.start_time = time.perf_counter()
        self.lastscreen = (time.perf_counter() - self.start_time, pyautogui.screenshot())
        with mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll), \
             keyboard.Listener(on_press=self.on_press, on_release=self.on_release):
            while self.running:
                self.lastscreen = (time.perf_counter() - self.start_time, pyautogui.screenshot())
        self.movelistener.stop()
        print("Monitoring has finished, we are preparing the final data file ...")
        # Saving data at the end
        data_df = pd.DataFrame(self.data, columns =['timestamp', 'img_path', 'px', 'py', 'event', 'trajectory'])
        data_df.to_csv(self.sample_folder + 'raw_pcdata.csv', index=False)
        # Zipping data
        print('Compressing data into a zip file ... it can take some time')
        shutil.make_archive(self.base_folder + self.sample_folder.split('/')[1], 'zip', self.sample_folder)

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
        if dx == 0 and dy == 0:
            self.logger.info('Something weird happens both dx and dy are zero')
        else: 
            if dy != 0:
                self.savedata(px, py, 
                            event=self.vscrolls[math.copysign(1,dy)] + '_' + str(abs(dy)), 
                            trajectory=self.moves)
            if dx != 0:
                self.savedata(px, py, 
                            event=self.hscrolls[math.copysign(1,dx)] + '_' + str(abs(dx)), 
                            trajectory=self.moves)

    
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
        temp_row = pd.DataFrame([self.data[-1]]) 
        with open(self.sample_folder + 'rawpcdata_temp.csv', 'a') as f:
            temp_row.to_csv(f, index=False, header=False, lineterminator='\n')
        if self.print_events:
            print(timestamp, event)
        self.counter += 1
        self.moves = []

    def wait_esc(self, key):
        if key != keyboard.Key.esc: 
            return True
        return False
    
    def locks_checking(self): 
        if keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._win32':
            locks = win11.LockStates()
            locks.reset_all()
        elif keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._xorg':
            while ubuntu.check_locks(): # Stop execution until caps and num locks are off
                time.sleep(2)
                os.system('clear')

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
        new_folder_name = "sample{:03d}".format(highest_num + 1)
        new_folder_path = os.path.join(path, new_folder_name)
        os.makedirs(new_folder_path)
        return new_folder_path
    
    def savemetada(self):
        date = str(datetime.datetime.now()).split('.')[0].replace(':','-').replace(' ','_')
        metadatafile = open(self.sample_folder + 'metadata.txt', 'w')
        os_language_encoding = locale.getlocale()
        ip_info = self.get_ip_info()
        if keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._win32':
            keyboard_language = win11.get_keyboard_language()
        elif keyboard.Key.__dict__['__module__'] == 'pynput.keyboard._xorg':
            keyboard_language = ubuntu.get_keyboard_language()
        metadata = ['date: ' + date + '\n',
                    'node name: ' + platform.node() + '\n', 
                    'os: ' + platform.system() + '\n', 
                    'version: ' + platform.version() + '\n', 
                    'release: ' + platform.release() + '\n', 
                    'platform: ' + platform.platform() + '\n', 
                    'processor: ' + platform.processor() + '\n',

                    'keyboard_language: ' + keyboard_language + '\n', 
                    'os_language: ' + os_language_encoding[0] + '\n', 
                    'os_encoding: ' + os_language_encoding[1] + '\n', 

                    'ip: ' + ip_info["ip"] + '\n', 
                    "hostname: " + ip_info["hostname"] + '\n', 
                    "city: " + ip_info["city"] + '\n', 
                    "region: " + ip_info["region"] + '\n', 
                    "country: " + ip_info["country"] + '\n', 
                    "loc: " + ip_info["loc"] + '\n', 
                    "org: " + ip_info["org"] + '\n', 
                    "postal: " + ip_info["postal"] + '\n', 
                    "timezone: " + ip_info["timezone"] + '\n', 
                    "readme: " + ip_info["readme"] + '\n', 
                    ] 
        metadatafile.writelines(metadata)
        metadatafile.close()

    def get_ip_info(self):
        ip_info = {"ip": '',
                "hostname": '',
                "city": '',
                "region": '',
                "country": '',
                "loc": '',
                "org": '',
                "postal": '',
                "timezone": '',
                "readme": '',}
        try:
            result = subprocess.run(['curl', 'ipinfo.io'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            ip_info = json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.logger.info(f"An error occurred: {e}")
            self.logger.info("Failed to retrieve IP information")
        return ip_info
    
    def creating_logger(self):
        logger = logging.getLogger('pcdata_logger')
        logger.setLevel(logging.INFO)  
        file_handler = logging.FileHandler(self.sample_folder + 'pcdata.log', mode='x')
        console_handler = logging.StreamHandler()
        file_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger 


    
