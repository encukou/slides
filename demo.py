import time
import asyncio
import dataclasses

print('sleep:', dir(asyncio.sleep(1)))

class MySleep:
    def __init__(self, delay):
        self.delay = delay

    def __await__(self):
        yield 1

print('—' * 50)

numbers = [0, 0]

def count(i, delay, limit=10):
    for n in range(limit):
        numbers[i] = n
        yield delay

async def acount(i, delay, limit=10):
    for n in range(limit):
        numbers[i] = n
        await MySleep(delay)

print('—' * 80)

events = [
    (0, 1, count(0, 1/10, limit=1000)),
    (0, 2, acount(1, 1/3, limit=1000).__await__()),
]
current_time = 0
while events:
    events.sort()
    if events:
        e_time, e_number, generator = events.pop(0)
        if e_time > current_time:
            time.sleep(e_time - current_time)
            current_time = e_time
        try:
            delay = next(generator)
        except StopIteration:
            pass
        else:
            print(numbers)
            events.append(
                (current_time+delay,
                 e_number,
                 generator)
            )

exit()
