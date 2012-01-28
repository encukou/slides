def debug(func):
    def wrapped(*args, **kwargs):
        rv = func(*args, **kwargs)
        print func.__name__, args, kwargs, '->', rv
        return rv
    return wrapped

@debug
def add(a, b):
    return a + b


add(1, 2)