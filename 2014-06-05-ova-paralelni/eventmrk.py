import random
import time
import asyncio

blinkers = []

def print_all():
    for blinker in blinkers:
        print(blinker, end='  ', flush=True)
        time.sleep(0.01)
    print(end='\r', flush=True)

class Blinker:
    def __init__(self):
        self._eyes = '(o.o)'
        self.odmrkni()

    def __str__(self):
        return self._eyes

    def set_eyes(self, new):
        self._eyes = new
        print_all()

    def mrkni(self, task=None):
        self.set_eyes('(-.-)')
        slp = asyncio.sleep(random.uniform(0.1, 0.5))
        asyncio.Task(slp).add_done_callback(self.odmrkni)

    def odmrkni(self, task=None):
        self.set_eyes('(o.o)')
        slp = asyncio.sleep(random.expovariate(1/5))
        asyncio.Task(slp).add_done_callback(self.mrkni)


blinkers.extend(Blinker() for i in range(10))

print_all()

asyncio.get_event_loop().run_forever()
