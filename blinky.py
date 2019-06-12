import asyncio as async_library
import warnings
import random


class Blinky:
    """A face like (o.o), animated using an async function"""

    def __init__(self, family, async_library):
        self.face = '(o.o)'
        self.family = family
        self.async_library = async_library

    def __str__(self):
        return self.face

    async def run(self):
        while True:
            await animation(self)

    async def show_face(self, new_face, delay):
        """Sets a new `face` string and keep it for `delay` seconds"""
        self.face = new_face
        print('\r', *self.family, end='\r')
        await self.async_library.sleep(delay)

async def animation(blinky):
    """Basic blinking animation"""
    await blinky.show_face('(-.-)', 0.1)
    await blinky.show_face('(o.o)', random.uniform(0.1, 1.5))
from blinky_animations import animation


async def run_all_blinkies():
    """Create a family of Blinkies and run their animations"""
    family = []
    family.extend(Blinky(family, async_library) for i in range(10))
    futures = [async_library.ensure_future(blinky.run()) for blinky in family]
    for future in futures:
        await future


async def count():
    await async_library.sleep(1)
    return 1

# Run it all

print()

try:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    async_library.run(run_all_blinkies())
except KeyboardInterrupt:
    pass

print()


# More fun:
from blinky_animations import animation
import demo as async_library
