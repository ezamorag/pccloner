import mouse
from pynput.mouse import Controller as mController
import time
import pyautogui

# https://github.com/boppreh/mouse/blob/7b773393ed58824b1adf055963a2f9e379f52cc3/mouse/_nixcommon.py

mC = mController()

print("Listening for scroll events.")
events = mouse.record()
print("Playing events in 3 seconds")
time.sleep(3)
for event in events:
    if isinstance(event,mouse.WheelEvent):
    	print(type(event.delta))
    	mC.scroll(0, event.delta)
    	#pyautogui.scroll(event.delta)
    	time.sleep(0.2)
  	
#mouse.play(events)
