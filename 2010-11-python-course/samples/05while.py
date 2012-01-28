a = b = 1
while b < 100:
    a, b = b, a + b
    print b
else:
    print "We're done"