import threading

def fireWorkThread(func,*args,**kwargs):
    thr = threading.Thread(target=func,args=args,kwargs=kwargs)
    thr.setDaemon(True)
    thr.start()
    return thr

