# pccloner
When you execute a task on your PC, it captures mouse and keyboard actions, including the cursor's position and a preceding screenshot. You can then replay the captured task whenever desired.
 
Supported Features:
* Capable of replaying double clicks and drag motions.
* Designed to replay almost all keystrokes (please report any unsupported key).
* Tested on Ubuntu 20.04 and Windows 11.
* Supports all hotkeys and sequences of hotkeys (please report any unsupported hotkey).

**Conditions for Optimal Performance**: The stored task must be replayed on the same computer, and the screen's initial state during replay should closely resemble the initially stored screen state.

Known Issues:
* On Ubuntu 20.04: 
    1) Occasionally, the collector registers one extra scroll action than required, which does not accurately replicate the task.
    2) At replaying time, pushing buttons to write over "Show Applications" does not work. The written words are sent to terminal. 
* On Windows 11:
    1) Scrolling isn't detected when using a touchpad; please use a mouse instead.
    2) The function (fn) key is not recognized, but detected.
    3) The alt_gr key can generate sequences of pairs (alt_gr + ctrl_l), leading to unnecessary storage of screenshots.
* Sometimes, in the process of minimizing a window, the size and location of the window are different w.r.t the original stored task. The replayer could fail in this case. 

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

## Usage
1. Write a python script with following lines:
```bash
File: collector.py

from pccloner.pcdata import Collector

if __name__ == '__main__':
    pc = Collector()
    data_df = pc.start()
```
2. Run the previous script ```python collector.py```
3. Press the ESC key to start recording. And don't forget to press again the ESC key to terminate the recording. This code will create a folder called "data" where it will save all the data related to your task.
4. Use the next code to replay your previous stored task ```python replayer.py -p [YOUR_PATH_TO_CSV_FILE]```. At replaying, you can exit the process pressing ESC. 
```bash
File: replayer.py

from glob import glob 
from pccloner.pctask import Replayer
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--csvpath', help="path to the task data")
parser.add_argument('--viz', action=argparse.BooleanOptionalAction, default=False, help="To visualize actions")
parser.add_argument('--screen', action=argparse.BooleanOptionalAction, help="True means that it uses the current screenshots to visualize actions")
args = parser.parse_args()

if not args.csvpath:
   print(glob('data/*/*.csv'))
   print('Select your stored task using the argument -p to give the path')
else: 
   sample = pd.read_csv(args.csvpath)
   task1 = Replayer(sample, data_dir='./')
   task1.execute(viz=args.viz, screen_flag=args.screen)
```
