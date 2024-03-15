# pccloner
 When you perform a task on your PC, it stores mouse and keyboard actions along with the concurrent cursor position (and preceding screenshot) and then you can replay the stored task when you want. 

 Current limitations: 
 * No drag actions 
 * Not pressed two keys o more at the same time
 * The replayer is not prepared for all events
 * It has been tested only on Ubuntu 20.04.
 * The initial screen state at replaying must be similar to the stored initial screen state. 
 * Your replayed task performs well on the same computer with similar conditions.  

## Authors
- [Erik Zamora](https://www.ezamorag.com)
## Installation
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pccloner
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

4. Use the following example to replay your previous stored task. 
```bash
from pccloner.pctask import Replayer
import pandas as pd

sample_paths = glob('./data/*/*.csv')   # Select the right path of your stored tasks
ix_sample = 2  # Select your stored task 

sample = pd.read_csv(sample_paths[ix_sample], index_col=0)
task1 = Replayer(sample, data_dir='./')
task1.execute()
```