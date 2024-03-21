from glob import glob 
from pccloner.pctask import Replayer
import pandas as pd

ix_sample = 1
sample_paths = glob('data/*/*.csv')
sample = pd.read_csv(sample_paths[ix_sample], index_col=0)
task1 = Replayer(sample, data_dir='../')
task1.execute(viz=True, screen_flag=True)