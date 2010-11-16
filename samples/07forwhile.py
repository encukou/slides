lst = [1, 2, 3]

for i in lst:
    print i


iterator = iter(lst)
while True:
    try:
        i = iterator.next()
    except StopIteration:
        break
    else:
        print i
