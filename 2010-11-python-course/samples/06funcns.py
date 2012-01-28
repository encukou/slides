a, b, c, d = None, None, None, None

def func(a):
    global b
    c = b = 3 * a
    return a, b, c, d

assert func(1) == (1, 3, 3, None)
assert (a, b, c, d) == (None, None, 3, None)
