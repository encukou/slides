import time
import contextvars
from heapq import heappush, heappop


loop = contextvars.ContextVar('loop')


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
        state = loop.get()
        state.tasks.extend(self.waiters)

    def __await__(self):
        if self.state == 'pending':
            yield self
        return self._value


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
    return context.run(_run_in_context, task)

def _run_in_context(task):
    state = State()
    loop.set(state)

    main_future = ensure_future(task)
    while main_future.state == 'pending':
        state.tasks.sort()
        task = state.tasks.pop(0)
        task_time, task_number, coro, future = task
        if task_time > state.time:
            time.sleep(task_time - state.time)
            state.time = task_time
        try:
            awaitable = next(coro)
        except StopIteration as e:
            future.set_result(e.value)
        else:
            if isinstance(awaitable, float):
                next_time = state.time + awaitable
                task = next_time, task_number, coro, future
                state.tasks.append(task)
            elif isinstance(awaitable, Future):
                awaitable.waiters.append(task)
            else:
                raise TypeError(awaitable)

    return main_future._value


def ensure_future(task):
    try:
        state = loop.get()
    except LookupError:
        raise RuntimeError('no active loop')

    task_number = next(state.task_numbers)
    future = Future()
    task = 0, task_number, task.__await__(), future
    state.tasks.append(task)
    return future


class sleep:
    def __init__(self, delay):
        self.delay = float(delay)

    def __await__(self):
        yield self.delay


async def add(a, b):
    print('...')
    await sleep(1)
    return a + b

print(run(add(1, 2)))

exit()
