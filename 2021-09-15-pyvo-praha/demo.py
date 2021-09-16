from presentation import Matrix, Vector, Scalar, sin, cos, draw, explain
from data import face_points, face_lines, cube_lines, eevee_triangles, black, gray, red, green, blue, yellow, cyan, magenta, white
import numpy

mat_identity = Matrix([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
])
zoom = Scalar(1)
mat_zoom = Matrix([
    [zoom, 0, 0, 0],
    [0, zoom, 0, 0],
    [0, 0, zoom, 0],
    [0, 0, 0, 1],
])
angle_y = Scalar()
rot_y = Matrix([
    [cos(angle_y), 0, sin(angle_y), 0],
    [0, 1, 0, 0],
    [-sin(angle_y), 0, cos(angle_y), 0],
    [0, 0, 0, 1],
])
angle_x = Scalar()
rot_x = Matrix([
    [1, 0, 0, 0],
    [0, cos(angle_x), sin(angle_x), 0],
    [0, -sin(angle_x), cos(angle_xi), 0],
    [0, 0, 0, 1],
])
explain(rot_y)

point = Vector([1, 2, 3, 1])

with rot_x @ rot_y @ mat_zoom:
    for a, b, c, n in eevee_triangles:
        draw.polygon(a, b, c)


