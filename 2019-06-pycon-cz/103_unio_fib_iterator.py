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

iterator = fib(0, 1/10)
print(iterator)
print(next(iterator), numbers)
print(next(iterator), numbers)
print(next(iterator), numbers)
print(next(iterator), numbers)
print(next(iterator), numbers)
print(next(iterator), numbers)

while True:
    i = next(iterator)
    print(i, numbers)

#for i in fib(0, 1/10):
    #print(numbers)

#for i in fib(1, 1/3):
    #print(numbers)


exit(0)
