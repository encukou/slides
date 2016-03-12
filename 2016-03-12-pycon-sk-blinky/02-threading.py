import random
import time
import threading

blinkies = []
def print_blinkies():
    print(*blinkies, sep=' ', end='\r')




class Blinky:
    def __init__(self):
        self._face = '(o.o)'

    def __str__(self):
        return self._face

    def set_face(self, new):
        self._face = new
        print_blinkies()

    def run(self):
        while True:
            self.set_face('(-.-)')
            time.sleep(random.uniform(0.05, 0.1))
            self.set_face('(o.o)')
            time.sleep(random.expovariate(1/2))

blinkies = [Blinky() for i in range(9)]

for blinky in blinkies:
    threading.Thread(target=blinky.run).start()
