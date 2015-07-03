import sys
import threading

def thrmain():
    return 69

thr = threading.Thread(target=thrmain)
thr.start()
thr.join()

