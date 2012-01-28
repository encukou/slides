file = open('somefile.txt')
try:
    for line in file:
        # Print first letter of the line
        print line[0]
finally:
    file.close()
