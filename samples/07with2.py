from threading import Lock

lock = Lock()

def threadsafeFunction(a, b, c):
    with lock:
        doSomething()
