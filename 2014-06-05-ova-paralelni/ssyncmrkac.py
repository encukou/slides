import random
import time


class Blinker:
    def set_eyes(self, eyes):
        print(eyes, end='\r')

    def run(self):
        while True:
            self.set_eyes('(o.o)')
            time.sleep(random.uniform(0.5, 1))
            self.set_eyes('(-.-)')
            time.sleep(random.uniform(0.1, 0.5))


blinker = Blinker()
blinker.run()
