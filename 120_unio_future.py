import time

class sleep:
    def __init__(self, delay):
        self.delay = delay

    def __await__(self):
        yield self.delay

class Lock:
    def __init__(self):
        self._awaited_future = None

    def locked(self):
        return self._awaited_future != None

    async def __aenter__(self):
        while self._awaited_future:
            await self._awaited_future
        self._awaited_future = Future()

    async def __aexit__(self, *args):
        self._awaited_future.set_result(0)
        self._awaited_future = None


class Future():
    def __init__(self):
        self.state = 'pending'
        self.waiters = []

    def set_result(self, value):
        self.state = 'completed'
        self._value = value
        tasks.extend(self.waiters)

    def __await__(self):
        if self.state == 'pending':
            yield self
        return self._value


# Task tuples: (scheduled_time, task_number, iterator)
tasks = []

next_task_number = 0

def create_task(awaitable):
    global next_task_number
    next_task_number += 1
    future = Future()
    task = current_time, next_task_number, awaitable.__await__(), future
    tasks.append(task)
    return future

current_time = 0
def run(task):
    global current_time
    main_future = create_task(task)
    while main_future.state == 'pending':
        tasks.sort()
        task = tasks.pop(0)
        scheduled_time, task_number, iterator, future = task
        if scheduled_time > current_time:
            time.sleep(scheduled_time - current_time)
            current_time = scheduled_time
        try:
            delay = next(iterator)
        except StopIteration as e:
            future.set_result(e.value)
        else:
            if isinstance(delay, Future):
                delay.waiters.append(task)
            else:
                task = current_time + delay, task_number, iterator, future
                tasks.append(task)
    return main_future._value


async def add(a, b):
    await sleep(0.1)
    return a + b

print(run(add(1, 2)))

#exit()
