import time

print('—' * 50)

numbers = [0, 0]

def count(i, delay, limit=10):
    for n in range(limit):
        numbers[i] = n
        yield delay

print('—' * 80)

events = [
    (0, 1, count(0, 1/10, limit=1000)),
    (0, 2, count(1, 1/3, limit=1000)),
]
current_time = 0
while events:
    events.sort()
    if events:
        e_time, e_number, generator = events.pop(0)
        if e_time > current_time:
            time.sleep(e_time - current_time)
            current_time = e_time
        try:
            delay = next(generator)
        except StopIteration:
            pass
        else:
            print(numbers)
            events.append(
                (current_time+delay,
                 e_number,
                 generator)
            )

exit(0)
print('—' * 80)

generators = [count(0, 1/10), count(1, 1/3)]
while True:
    for generator in generators:
        try:
            delay = next(generator)
        except StopIteration:
            break
        else:
            print(delay, numbers)


print('—' * 80)

generator = count(0, 1/10)
while True:
    try:
        delay = next(generator)
    except StopIteration:
        break
    else:
        print(delay, numbers)


#for delay in count(0, 1/10):
    #print(numbers)
    #time.sleep(delay)


#for delay in count(1, 1/3):
    #print(numbers)
    #time.sleep(delay)


exit()
