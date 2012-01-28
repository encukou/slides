def fibonacci(max=None):
    a = 0
    b = 1
    while (not max) or (a <= max):
        yield a
        a, b = b, a + b
