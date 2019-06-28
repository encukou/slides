print('—'*50)

def fib(limit=100):
    a = b = 1
    while a < limit:
        yield a
        a, b = b, a + b

for i in fib():
    print(i)


exit(0)
