import random
import threading
import time

lock = threading.Lock()

def print_blinkies(family):
    with lock:
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

    def show_face(self, new_face, delay):
        self.face = new_face
        print_blinkies(self.family)
        time.sleep(delay)

    def run(self):
        while True:
            self.show_face('(-.-)', 0.1)
            self.show_face('(o.o)', random.uniform(0.1, 1.5))


family = []
family.extend(Blinky(family) for i in range(10))

for blinky in family:
    threading.Thread(target=blinky.run).start()
