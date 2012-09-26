import os
import math

f = raw_input("Zadej funkci: ")

for x in range(5):
    print "x = %s, y = %s" % (x, eval(f))
