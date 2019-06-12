import time
import contextvars
from heapq import heappush, heappop


loop = contextvars.ContextVar('loop')


class State:
    def __init__(self):
        self.tasks = []
        self.time = 0
        self.task_numbers = self.counter()

    def counter(self):
        i = 0
        while True:
            yield i
            i += 1

def run(task):
    context = contextvars.copy_context()
    state = State()
    context.run(loop.set, state)
    context.run(ensure_future, task)
    while state.tasks:
        state.tasks.sort()
        task_time, task_number, coro = heappop(state.tasks)
        if task_time > state.time:
            time.sleep(task_time - state.time)
            state.time = task_time
        try:
            awaitable = context.run(next, coro)
        except StopIteration:
            pass
        else:
            if isinstance(awaitable, float):
                next_time = state.time + awaitable
                heappush(state.tasks, (next_time, task_number, coro))


def ensure_future(task):
    try:
        state = loop.get()
    except LookupError:
        raise RuntimeError('no active loop')

    task_number = next(state.task_numbers)
    heappush(state.tasks, (0, task_number, task.__await__()))
    return sleep(1)


class sleep:
    def __init__(self, delay):
        self.delay = float(delay)

    def __await__(self):
        yield self.delay
