import random
import time
import asyncio

blinkies = []
def print_blinkies():
    print(*blinkies, sep=' ', end='\r')

class Blinky:
    def __init__(self):
        self._face = '(o.o)'
        asyncio.Task(self.run())

    def __str__(self):
        return self._face

    def set_face(self, new):
        self._face = new
        print_blinkies()

    async def run(self):
        while True:
            self.set_face('(-.-)')
            await asyncio.sleep(random.uniform(0.05, 0.1))
            self.set_face('(o.o)')
            await asyncio.sleep(random.expovariate(1/2))



blinkies = [Blinky() for i in range(9)]

asyncio.get_event_loop().run_forever()
