#! /usr/bin/python3

import random
import time
import asyncio

def print_all():
    print(*blinkers, sep='  ', end='\r')

class Blinker:
    def __init__(self):
        self._eyes = '(o.o)'
        asyncio.Task(self.run())

    def __str__(self):
        return self._eyes

    def set_eyes(self, new):
        self._eyes = new
        print_all()

    @asyncio.coroutine
    def run(self, task=None):
        while True:
            yield from asyncio.sleep(random.uniform(0.05, 0.3))
            self.set_eyes('(o.o)')
            yield from asyncio.sleep(random.expovariate(1/3))
            self.set_eyes('(-.-)')

blinkers = [Blinker() for i in range(10)]

asyncio.get_event_loop().run_forever()
