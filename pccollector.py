from src.pccloner.pcdata import Collector

if __name__ == '__main__':
    pc = Collector(print_events=False, saving_end = False)
    pc.start()
