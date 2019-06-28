from presentation import Vector
from readstl import read_stl


face_points = (
    Vector([7, 7, 1]),
    Vector([3, 7, 1]),
    Vector([7, 4, 1]),
    Vector([3, 4, 1]),
    Vector([6.5, 3.5, 1]),
    Vector([3.5, 3.5, 1]),
    Vector([5.8, 3.2, 1]),
    Vector([4.2, 3.2, 1]),
    Vector([5.2, 3, 1]),
    Vector([4.7, 3, 1]),
)

face_lines = (
    (Vector([8, 8, 1]), Vector([8, 2, 1])),
    (Vector([8, 2, 1]), Vector([2, 2, 1])),
    (Vector([2, 2, 1]), Vector([2, 8, 1])),
    (Vector([2, 8, 1]), Vector([8, 8, 1])),
)


cube_lines = (
    (Vector([5, 5, 5, 1]), Vector([-5, 5, 5, 1])),
    (Vector([5, 5, 5, 1]), Vector([5, -5, 5, 1])),
    (Vector([-5, 5, 5, 1]), Vector([-5, -5, 5, 1])),
    (Vector([5, -5, 5, 1]), Vector([-5, -5, 5, 1])),

    (Vector([5, 5, -5, 1]), Vector([-5, 5, -5, 1])),
    (Vector([5, 5, -5, 1]), Vector([5, -5, -5, 1])),
    (Vector([-5, 5, -5, 1]), Vector([-5, -5, -5, 1])),
    (Vector([5, -5, -5, 1]), Vector([-5, -5, -5, 1])),

    (Vector([5, 5, 5, 1]), Vector([5, 5, -5, 1])),
    (Vector([5, -5, 5, 1]), Vector([5, -5, -5, 1])),
    (Vector([-5, 5, 5, 1]), Vector([-5, 5, -5, 1])),
    (Vector([-5, -5, 5, 1]), Vector([-5, -5, -5, 1])),
)


# Model from: https://www.thingiverse.com/thing:2931434/
# Low-Poly Eevee by FLOWALISTIK is licensed under the
# Creative Commons - Attribution - Non-Commercial - Share Alike license. 
eevee_triangles = read_stl('low-poly-eevee.STL')
