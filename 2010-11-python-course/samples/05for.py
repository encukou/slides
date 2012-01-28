iterable = "a b c d skip e f end not_printed".split()
for value in iterable:
    print "value = ", value
else:
    print "This executes at the end"
    print "(if a break/raise didn't end the loop)"