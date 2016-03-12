import random
import time
import asyncio

blinkies = []
def print_blinkies():
    print(*blinkies, sep=' ', end='\r')

class Blinky:
    def __init__(self):
        self.open_eyes()

    def __str__(self):
        return self._face

    def set_face(self, new):
        self._face = new
        print_blinkies()

    def close_eyes(self, task=None):
        self.set_face('(-.-)')
        task = asyncio.Task(asyncio.sleep(random.uniform(0.05, 0.1)))
        task.add_done_callback(self.open_eyes)

    def open_eyes(self, task=None):
        self.set_face('(o.o)')
        task = asyncio.Task(asyncio.sleep(random.expovariate(1/2)))
        task.add_done_callback(self.close_eyes)

blinkies = [Blinky() for i in range(9)]

asyncio.get_event_loop().run_forever()
