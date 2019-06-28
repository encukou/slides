import time

print('—'*50)

numbers = [0, 0]

def fib(i, delay=0, limit=1e9):
    a = b = 1
    while a < limit:
        numbers[i] = a
        a, b = b, a + b
        yield from sleep(delay)
    return a

def sleep(delay):
    yield delay/2
    yield delay/2

# Task tuples: (scheduled_time, task_number, iterator)
tasks = [
    (0, 1, fib(0, 1/10)),
    (0, 2, fib(1, 1/3)),
]
current_time = 0
while tasks:
    tasks.sort()
    task = tasks.pop(0)
    scheduled_time, task_number, iterator = task
    if scheduled_time > current_time:
        time.sleep(scheduled_time - current_time)
        current_time = scheduled_time
    try:
        delay = next(iterator)
    except StopIteration as e:
        pass
    else:
        task = current_time + delay, task_number, iterator
        tasks.append(task)

    # loop body
    print(numbers)


exit(0)
