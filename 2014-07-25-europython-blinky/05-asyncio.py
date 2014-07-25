import random
import time
import asyncio

def print_blinkies():
    print(*blinkies, sep=' ', end='\r')

blinkies = []

class Blinky:
    def __init__(self):
        self._face = '(o.o)'
        asyncio.Task(self.run())

    def __str__(self):
        return self._face

    def set_face(self, new):
        self._face = new
        print_blinkies()

    @asyncio.coroutine
    def run(self):
        while True:
            self.set_face('(-.-)')
            yield from asyncio.sleep(random.uniform(0.05, 0.1))
            self.set_face('(o.o)')
            yield from asyncio.sleep(random.expovariate(1/2))


blinkies = [Blinky() for i in range(15)]

asyncio.get_event_loop().run_forever()

