
def count(obj, num):
    for i in range(num):
        yield '{} #{}'.format(obj, i+1)
    return num

def apples_oranges():
    yield from count('apple', 3)
    yield from count('orange', 5)

for message in apples_oranges():
    print(message)
