from glob import glob 
from pccloner.pctask import Replayer
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--csvpath', help="path to the task data")
parser.add_argument('--viz', action=argparse.BooleanOptionalAction, default=False, help="To visualize actions")
parser.add_argument('--screen', action=argparse.BooleanOptionalAction, help="True means that it uses the current screenshots to visualize actions")
parser.add_argument('--mousemoves', action=argparse.BooleanOptionalAction, help="True means that cursor movements before each event is performed (except to drags events)")

args = parser.parse_args()

if not args.csvpath:
   print(glob('data/*/*.csv'))
   print('Select your stored task using the argument -p to give the path')
else: 
   sample = pd.read_csv(args.csvpath)
   task1 = Replayer(sample, data_dir='./')
   task1.execute(viz=args.viz, screen_flag=args.screen, mousemoves_flag=args.mousemoves)
