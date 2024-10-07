# pccloner
When you execute a task on your PC, it captures mouse and keyboard actions, including the cursor's position and a preceding screenshot. You can then replay the captured task whenever desired.
 
Supported Features:
* Capable of replaying double clicks and drag motions.
* Designed to replay almost all keystrokes (please report any unsupported keys).
* Tested on Ubuntu 20.04 and Windows 11.
* It records and replays the cursor's trajectory before each keyboard and mouse event.

**Conditions for Optimal Performance**: The stored task must be replayed on the same computer, and the screen's initial state during replay should closely resemble the initial state when the task was recorded.

Known Issues:
* On Ubuntu 20.04: 
    1) Occasionally, the collector registers one extra scroll action than required, which does not accurately replicate the task.
    2) During replay, attempting to type over "Show Applications" does not work; the input is sent to the terminal instead.
    3) If you use a hidden taskbar, the replayer cannot activate it, even if this action was recorded. 
    4) The 'Caps Lock' key is saved correctly, but it is not triggered during the task replay.
* On Windows 11:
    1) Scrolling isn't detected when using a touchpad; please use a mouse instead.
    2) The function (fn) key is detected but not recognized.
    3) The alt_gr key can generate sequences of pairs (alt_gr + ctrl_l), leading to the unnecessary storage of screenshots.
* General issues:
    1) Sometimes, when minimizing a window, the size and location of the window differ from the original stored task, which could cause the replayer to fail.
   

## Authors
- [Erik Zamora](https://www.ezamorag.com)
## Installation
```bash
pip install pccloner
```
On ubuntu: it requires to install gnome-screenshot.
```bash
sudo apt install gnome-screenshot
```

## Basic usage
1. Download and run the file ```python testing.py``` in your environment where pcpcloner is installed. 
2. Press the ESC key to start recording. To stop the recording, press and release the ESC key three times consecutively. The program will create a folder called 'data' where all task-related data will be saved. 
3. If you want to replay the task, type 'yes' when prompted with 'Do you want to replay the previous task? and press enter. 

## Advanced usage
1. Write a python script with following lines:
```bash
File: pccollector.py

from pccloner.pcdata import Collector

if __name__ == '__main__':
    pc = Collector(print_events=False, saving_end = False)
    pc.start()
```
2. Run the previous script ```python collector.py```
3. Press the ESC key to start recording. And don't forget to terminate the recording by pressing and releasing the ESC key three times consecutively. This code will create a folder called "data" where it will save all the data related to your task.
4. Use the next code to replay your previous stored task ```python replayer.py -p [YOUR_PATH_TO_CSV_FILE]```. At replaying, you can exit the process pressing ESC. 
```bash
File: replayer.py

from glob import glob 
from pccloner.pctask_pr import Replayer
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--csvpath', help="path to the task data")
parser.add_argument('--viz', action=argparse.BooleanOptionalAction, default=False, help="To visualize actions")
parser.add_argument('--screen', action=argparse.BooleanOptionalAction, help="True means that it uses the current screenshots to visualize actions")
parser.add_argument('--mousemoves', action=argparse.BooleanOptionalAction, help="True means that cursor movements before each event is performed (except to drags events)")

args = parser.parse_args()

if not args.csvpath:
   print(glob('data/*/raw_pcdata.csv'))
   print('Select your stored task using the argument -p to give the path')
else: 
   sample = pd.read_csv(args.csvpath)
   task1 = Replayer(sample, data_dir='./')
   task1.execute(viz=args.viz, screen_flag=args.screen, mousemoves_flag=args.mousemoves)
```

## Using apps 
You can download the executable programs without installing the pccloner PyPI package. These apps are for both Windows and Ubuntu users. You can find them in the 'dist' folder in this repository. In an Ubuntu terminal, run ```./pccloner_applinux_[VERSION]```, then activate it by pressing the ESC key once, and deactivate it by pressing and releasing the ESC key three times consecutively. On Windows, simply run the file ```pccloner_appwin_[VERSION].exe``` by double-clicking it, then activate and deactivate it as previously mentioned."