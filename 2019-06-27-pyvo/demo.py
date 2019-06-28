from presentation import Matrix, Vector, Scalar, sin, cos, draw, explain
from data import face_points, face_lines, cube_lines, eevee_triangles
import numpy

scale = Scalar(2)

m = Matrix(
    [[scale, 0, 0, 0],
     [0, scale, 0, -3],
     [0, 0, scale, 0],
     [0, 0, 0, 1]]
)

xr = Scalar(0)

m @= Matrix(
    [[1, 0,        0,       0],
     [0,  cos(xr), sin(xr), 0],
     [0, -sin(xr), cos(xr), 0],
     [0, 0,        0,       1]]
)

yr = Scalar(0)

m @= Matrix(
    [[cos(yr),  0, sin(yr),  0],
     [0,        1, 0,        0],
     [-sin(yr), 0, cos(yr), 0],
     [0,        0, 0,       1]]
)

zr = Scalar(0)

m @= Matrix(
    [[cos(zr), sin(zr), 0, 0],
     [-sin(zr), cos(zr), 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, 1]]
)

with m:
    for a, b, c, n in eevee_triangles:
        draw.polygon(a, b, c)
