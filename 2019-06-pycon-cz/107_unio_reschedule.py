import time

print('—'*50)

numbers = [0, 0]

def fib(i, delay=0, limit=1e9):
    a = b = 1
    while a < limit:
        numbers[i] = a
        a, b = b, a + b
        yield delay
    return a

# Task tuples: (scheduled_time, iterator)
tasks = [
    (0, fib(0, 1/10)),
    (0, fib(1, 1/3)),
]
current_time = 0
while tasks:
    task = tasks.pop(0)
    scheduled_time, iterator = task
    if scheduled_time > current_time:
        time.sleep(scheduled_time - current_time)
        current_time = scheduled_time
    try:
        delay = next(iterator)
    except StopIteration as e:
        break

    task = current_time + delay, iterator
    tasks.append(task)

    # loop body
    print(numbers)


exit(0)
