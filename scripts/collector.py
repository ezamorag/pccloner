from pccloner.pcdata import Collector

if __name__ == '__main__':
    pc = Collector()
    pc.start()

### Optional
import sys, subprocess
if sys.platform == "linux" or sys.platform == "linux2":
    subprocess.run(['sudo', 'chown', '-R', 'ezamorag:ezamorag', '../data/'])

