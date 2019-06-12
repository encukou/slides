import random
import asyncio as async_library
import time

from basic_animations import animation

print()

def print_blinkies(family):
    for blinky in family:
        print(blinky, end=' ')
    print(end='\r')

class Blinky:
    def __init__(self, family, async_library):
        self.face = '(o.o)'
        self.family = family
        self.async_library = async_library

    def __str__(self):
        return self.face

    async def show_face(self, new_face, delay):
        self.face = new_face
        print_blinkies(self.family)
        await self.async_library.sleep(delay)

    async def run(self):
        while True:
            await animation(self)


async def run_all():
    family = []
    family.extend(Blinky(family, async_library) for i in range(10))

    tasks = []
    for blinky in family:
        task = async_library.create_task(blinky.run())
        tasks.append(task)

    for task in tasks:
        await task


async_library.run(run_all())

print()
