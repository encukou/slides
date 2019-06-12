import time

print('—'*50)

numbers = [0, 0]

def fib(i, delay=0, limit=100):
    a = b = 1
    while a < limit:
        numbers[i] = a
        yield a
        a, b = b, a + b
        time.sleep(delay)
    return a

iterators = [
    fib(0, 1/10),
    fib(1, 1/3),
]

while True:
    for iterator in iterators:
        try:
            i = next(iterator)
        except StopIteration as e:
            break

        # loop body
        print(numbers)


exit(0)
