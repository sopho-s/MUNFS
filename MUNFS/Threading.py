import threading

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def classthreaded(cls):
    def wrapper(*args, **kwargs):
        returnclass = cls(*args, **kwargs)
        thread = threading.Thread(target=returnclass.Run)
        thread.start()
        return thread, returnclass
    return wrapper