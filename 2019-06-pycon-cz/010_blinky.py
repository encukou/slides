import random
import time

class Blinky:
    def __init__(self):
        self.face = '(o.o)'

    def __str__(self):
        return self.face

    def show_face(self, new_face, delay):
        self.face = new_face
        print('\r', self, end='\r')
        time.sleep(delay)

    def run(self):
        while True:
            self.show_face('(-.-)', 0.1)
            self.show_face('(o.o)', random.uniform(0.1, 1.5))


blinky = Blinky()
blinky.run()
