import time

print('—'*50)

def fib(delay=0, limit=100):
    a = b = 1
    while a < limit:
        yield a
        a, b = b, a + b
        time.sleep(delay)

for i in fib(1/10):
    print(i)


exit(0)
