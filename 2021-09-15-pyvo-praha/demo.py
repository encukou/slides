from presentation import Matrix, Vector, Scalar, sin, cos, draw, explain
from data import face_points, face_lines, cube_lines, eevee_triangles
import numpy

m = Matrix([
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
])

explain(m)

point = Vector([3, 2, 1])
explain(point)

draw(point)
