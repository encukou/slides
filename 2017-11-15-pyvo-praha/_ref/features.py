
def add(a, b):
    return a + b


print(add(1, 2))

###

import dataclasses

@dataclasses.dataclass
class Sprite:
    x: float
    y: float
    width: float
    height: float
    color: tuple = (0, 0, 0)

sprite = Sprite(0, 0, 64, 128, (1, 0, 0))
sprite2 = Sprite(20, 10, 2, 2)
print(sprite)

print(sprite == sprite2)

###

def __getattr__(name):
    return '<{}>'.format(name)
