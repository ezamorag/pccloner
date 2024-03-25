from glob import glob 
from src.pccloner.pctask import Replayer
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--csvpath', help="path to the task data")
parser.add_argument('--viz', action=argparse.BooleanOptionalAction, default=False, help="To visualize actions")
parser.add_argument('--screen', action=argparse.BooleanOptionalAction, help="True means that it use the current screenshots to visualize actions")
args = parser.parse_args()

if not args.csvpath:
   print(glob('data/*/*.csv'))
else: 
   sample = pd.read_csv(args.csvpath, index_col=0)
   task1 = Replayer(sample, data_dir='./')
   task1.execute(viz=args.viz, screen_flag=args.screen)
