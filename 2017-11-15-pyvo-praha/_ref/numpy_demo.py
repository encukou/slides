import numpy

a = numpy.array([
    [1, 0, 1],
    [0, 1, 0],
])

b = numpy.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
])

print(b[..., 0])
