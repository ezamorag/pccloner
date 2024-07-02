from pccloner.pcdata import Collector
from glob import glob 
from pccloner.pctask import Replayer
import pandas as pd

if __name__ == '__main__':
    pc = Collector(print_events=True)
    data_df = pc.start()
    
    input('Press enter!')
    print()
    x = input('Do you want to replay the previous task? ("yes"+enter / enter)')
    print(x)
    if x == "yes":
        csv_paths = glob('data/*/raw_pcdata.csv')
        print(csv_paths)
        if csv_paths != []: 
            csv_paths.sort()
            sample = pd.read_csv(csv_paths[-1])
            task1 = Replayer(sample, data_dir='./')
            task1.execute(viz=False, screen_flag=False, mousemoves_flag=True)
        else:
            print('csv file was not found!')
