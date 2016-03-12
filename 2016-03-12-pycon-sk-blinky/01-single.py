import random
import time



def print_blinky(blinky):
    print(blinky, end='\r')




class Blinky:
    def __init__(self):
        self._face = '(o.o)'

    def __str__(self):
        return self._face

    def set_face(self, new):
        self._face = new
        print_blinky(self)

    def run(self):
        while True:
            self.set_face('(-.-)')
            time.sleep(random.uniform(0.05, 0.1))
            self.set_face('(o.o)')
            time.sleep(random.uniform(0.5, 1))

Blinky().run()



