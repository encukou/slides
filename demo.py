from presentation import Array, Vector, Scalar, sin, cos, draw, explain

xy = Scalar(0.0)
θ = Scalar(0)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

rm = Array([[1, 0, 0, 0],
            [0, cos(θ), sin(θ), 0],
            [0, -sin(θ), cos(θ), 0],
            [0, 0, 0, 1]])

m @= rm

explain(m)

cube_lines = (
    (Vector([xy, 5, 5, 1]), Vector([-5, 5, 5, 1])),
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
for a, b in cube_lines:
    ma = m@a
    draw.line(ma, m@b)
    explain(ma)

exit()

m = Array([[1, 0, xy],
           [1, 2, xy],
           [0, 0, 1]])

tr = Array([[1, 0, -5],
            [0, 1, -5],
            [0, 0, 1]])

m = Array([[cos(xy), sin(xy), 0],
           [-sin(xy), cos(xy), 0],
           [0, 0, 1]])

point = Vector([3, 1, 1])

explain(point)

#draw.arrow(point, m @ point)

mat = m @ tr
explain(mat)

for point in (
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
):
    draw(point, color=draw.gray)
    rotated = mat @ point
    draw(rotated)

    explain(rotated)

explain(m@m)

#draw(point+point)
m @ m

point = Vector([-2, -8, 2, 1])

θ = Scalar(3.141/2)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

m @ m
m @ point

explain(m @ point)

exit()

print(m @ point)

draw(point)
draw.arrow(point, m @ point)
exit()
draw.polygon(point, m @ point, [-1,5, 0, 1])

θ = Scalar(3.141/2)

rot = Array([[cos(θ), sin(θ), 0],
             [-sin(θ), cos(θ), 0],
             [0, 0, 1]])

draw(rot @ point)

point = Vector([-2, -8, 2, 1])

draw(point)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

rm = Array([[1, 0, 0, 0],
            [0, cos(θ), sin(θ), 0],
            [0, -sin(θ), cos(θ), 0],
            [0, 0, 0, 1]])

rm2 = Array([[cos(θ), 0, sin(θ), 0],
             [0, 1, 0, 0],
             [-sin(θ), 0, cos(θ), 0],
             [0, 0, 0, 1]])

m = m @ rm2 @ rm

draw.line(point, m @ point)

from eevee import triangles

print(len(triangles))
for a, b, c, n in triangles[:1]:
    draw.polygon(m@a, m@b, m@c)
