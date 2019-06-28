import random
import unio as async_library
import time

from basic_animations import animation

print()

def print_blinkies(family):
    for blinky in family:
        print(blinky, end=' ')
    print(end='\r')

from philosophers import Philosopher as Blinky

async def run_all():
    family = []
    family.extend(Blinky(family, async_library) for i in range(5))

    tasks = []
    for blinky in family:
        task = async_library.create_task(blinky.run())
        tasks.append(task)

    for task in tasks:
        await task


async_library.run(run_all())

print()
