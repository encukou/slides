import time

class sleep:
    def __init__(self, delay):
        self.delay = delay

    def __await__(self):
        yield self.delay


# Task tuples: (scheduled_time, task_number, iterator)
tasks = []

next_task_number = 0

def create_task(awaitable):
    global next_task_number
    next_task_number += 1
    task = current_time, next_task_number, awaitable.__await__()
    tasks.append(task)

current_time = 0
def run(task):
    global current_time
    create_task(task)
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
