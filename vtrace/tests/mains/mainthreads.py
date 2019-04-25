import time
import threading

import main

if __name__ == '__main__':
    main.waitForTest()
    thr = threading.Thread(target=time.sleep, args=(0.1,))
    thr.start()
    thr.join()
    time.sleep(0.1)
    main.exitTest()
