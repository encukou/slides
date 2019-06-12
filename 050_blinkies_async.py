import random
import asyncio
import time

def print_blinkies(family):
    for blinky in family:
        print(blinky, end=' ')
        time.sleep(0.001)  # simulate print() taking more time
    print(end='\r')

class Blinky:
    def __init__(self, family):
        self.face = '(o.o)'
        self.family = family
        print_blinkies(family)

    def __str__(self):
        return self.face

    async def show_face(self, new_face, delay):
        self.face = new_face
        print_blinkies(self.family)
        await asyncio.sleep(delay)

    async def run(self):
        for i in range(3):
            await self.show_face('(-.-)', 0.1)
            await self.show_face('(o.o)', random.uniform(0.1, 1.5))
        await self.show_face('(×.×)', 0.1)


family = []
family.extend(Blinky(family) for i in range(10))

for blinky in family:
    asyncio.ensure_future(blinky.run())
