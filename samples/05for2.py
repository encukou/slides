iterable = "a b c d skip e f end not_printed".split()
for value in iterable:
    if value == 'skip':
        print "Skipping a value"
        continue
    print "value = ", value
    if value == 'end':
        print "Terminating printout"
        break