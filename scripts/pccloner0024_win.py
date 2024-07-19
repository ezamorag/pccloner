from pccloner.pcdata import Collector
from pccloner.pctask import Replayer
import pandas as pd
from glob import glob 

if __name__ == '__main__':
    pc = Collector(print_events=True)
    data_df = pc.start()
    
    input('Press enter!')
    print()
    x = input('Do you want to replay the previous task? ("yes"+enter / enter)')
    print(x)
    if x == "yes":
        csv_paths = glob('data/*/raw_pcdata.csv')
        csv_paths.sort()
        print(csv_paths)
        if csv_paths != []: 
            print(f'You are using this file: {csv_paths[-1]}')
            sample = pd.read_csv(csv_paths[-1])
            task1 = Replayer(sample, data_dir='./')
            task1.execute(viz=False, screen_flag=False, mousemoves_flag=True)
        else:
            print('csv file was not found!')
