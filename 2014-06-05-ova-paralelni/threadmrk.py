import random
import time
import threading

blinkers = []

def print_all():
    print(*blinkers, sep='  ', end='\r')

class Blinker:
    def __init__(self):
        self._eyes = '(o.o)'

    def __str__(self):
        return self._eyes

    def set_eyes(self, new):
        self._eyes = new
        print_all()

    def run(self):
        while True:
            self.set_eyes('(o.o)')
            time.sleep(random.expovariate(1/5))
            self.set_eyes('(-.-)')
            time.sleep(random.uniform(0.1, 0.5))


blinkers.extend(Blinker() for i in range(10))

for blinker in blinkers:
    threading.Thread(target=blinker.run).start()
