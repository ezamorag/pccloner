# pccloner
When you execute a task on your PC, it captures mouse and keyboard actions, including the cursor's position and a preceding screenshot. You can then replay the captured task whenever desired.
 
Supported Features:
* Capable of replaying double clicks and drag motions.
* Designed to replay almost all keystrokes (please report any unsupported key).
* Tested on Ubuntu 20.04.
* Supports all hotkeys and sequences of hotkeys (please report any unsupported hotkey).

**Conditions for Optimal Performance**: The stored task must be replayed on the same computer, and the screen's initial state during replay should closely resemble the initially stored screen state.

Known Issues:
* Occasionally, the collector records one additional scroll-down action than necessary. This produces not replaying well the task. 
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

pc = Collector()
pc.start()
```
2. Run the previous script. On Ubuntu: ```sudo [your python path here] collector.py```. Or on Windows: ```python collector.py```
3. Press the ESC key to start recording. And don't forget to press again the ESC key to terminate the recording. This code will create a folder called "data" where it will save all the data related to your task. Note: On Ubuntu, it is useful, not necesary, to change the permissions of the data folder with ```sudo chown -R $USER:$USER data/```

4. Use the following example to replay your previous stored task. At replaying, you can exit the process pressing ESC. 
```bash
from pccloner.pctask import Replayer
import pandas as pd

sample_paths = glob('./data/*/*.csv')   # Select the right path of your stored tasks
ix_sample = 2  # Select your stored task 

sample = pd.read_csv(sample_paths[ix_sample], index_col=0)
task1 = Replayer(sample, data_dir='./')
task1.execute()
```
