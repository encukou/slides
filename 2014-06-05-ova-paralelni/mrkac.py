import random
import time
import asyncio

blinkers = []

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
    def run(self):
        while True:
            yield from asyncio.sleep(random.expovariate(1/5))
            val = random.randrange(0, 10)
            if val == 1:
                for i in range(random.randint(2, 4)):
                    self.set_eyes('O.o )')
                    yield from asyncio.sleep(0.5)
                    self.set_eyes('(o.o)')
                    yield from asyncio.sleep(0.5)
                    self.set_eyes('( o.O')
                    yield from asyncio.sleep(0.5)
                    self.set_eyes('(o.o)')
                    yield from asyncio.sleep(0.5)
            elif val == 2:
                self.set_eyes('(^_^)')
                yield from asyncio.sleep(random.expovariate(1/3))
                self.set_eyes('(o.o)')
            elif val == 3:
                self.set_eyes('(~_~)')
                yield from asyncio.sleep(random.expovariate(1/50))
                self.set_eyes('(o.o)')
            elif val == 4:
                self.set_eyes('(O_O)')
                yield from asyncio.sleep(0.25 + random.expovariate(1))
                self.set_eyes('(o.o)')
            elif val == 5:
                for i in range(random.randint(1, 3)):
                    self.set_eyes('(o.-)')
                    yield from asyncio.sleep(random.uniform(0.3, 0.7))
                    self.set_eyes('(o.o)')
                    yield from asyncio.sleep(random.uniform(0.3, 0.7))
            elif val == 6:
                for i in range(random.randint(5, 20)):
                    self.set_eyes('(o_o)')
                    yield from asyncio.sleep(random.uniform(0.1, 0.2))
                    self.set_eyes('(o.o)')
                    yield from asyncio.sleep(random.uniform(0.1, 0.2))
            else:
                self.set_eyes('(-.-)')
                yield from asyncio.sleep(random.uniform(0.1, 0.5))
                self.set_eyes('(o.o)')

blinkers.extend(Blinker() for i in range(15))

print_all()

asyncio.get_event_loop().run_forever()
