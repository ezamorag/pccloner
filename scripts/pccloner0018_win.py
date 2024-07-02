from pccloner.pcdata import Collector
from glob import glob 
from pccloner.pctask import Replayer
import pandas as pd

if __name__ == '__main__':
    pc = Collector()
    data_df = pc.start()
    
    x = input('Do you want to replay this previous task? (y+enter / any+enter)')
    if x == 'y':
        csv_paths = glob('data/*/*.csv')
        if csv_paths != []: 
            csv_paths.sort()
            sample = pd.read_csv(csv_paths[-1])
            task1 = Replayer(sample, data_dir='./')
            task1.execute(viz=False, screen_flag=False, mousemoves_flag=True)
        else:
            print('csv file was not found!')
