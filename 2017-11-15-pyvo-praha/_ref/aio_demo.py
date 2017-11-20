import asyncio

async def count(obj, num):
    for i in range(num):
        print('{} #{}'.format(obj, i+1))
        await asyncio.sleep(0.1)
    return num

async def apples_oranges():
    total = 0
    total += await count('apple', 3)
    total += await count('orange', 5)
    return total

asyncio.ensure_future(count('...', 10))

loop = asyncio.get_event_loop()
result = loop.run_until_complete(apples_oranges())
print(result)
