from pathlib import Path
import struct
import numpy
from presentation import Vector

def read(file, nbytes):
    result = b''
    while nbytes:
        chunk = file.read(nbytes)
        if not chunk:
            raise EOFError()
        result += chunk
        nbytes -= len(chunk)
    return result

def read_number(f):
    return int.from_bytes(read(f, 4), 'little')

def read_xyz(f):
    x, z, y = struct.unpack('3f', read(f, 12))
    return x+45, y+0, z+200

def read_stl(filename):
    with Path(filename).open('rb') as f:
        print('55', read(f, 80))
        num_triangles = read_number(f)
        triangles = numpy.zeros((num_triangles, 4, 3))
        for i in range(num_triangles):
            normal, a, b, c = read_xyz(f), read_xyz(f), read_xyz(f), read_xyz(f)
            triangles[i] = a, b, c, normal
            read(f, 2)

    the_max = abs(triangles).max
    for axis in range(3):
        print(triangles[:, :, axis].mean())
        #triangles[:, :, axis] -= triangles[:, :, axis].mean()
        triangles[:, :, axis] /= the_max()

    triangles *= 10
    print(triangles)

    return [[Vector([*v, 1]) for v in row] for row in triangles]
