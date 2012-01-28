def func():
    return 1, 2

a, b = func()

table = {
        (2, 3): 'value',
        (3, 4): 'value2',
    }

print table[2, 3]
