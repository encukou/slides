from presentation import Array, Vector, Scalar, sin, cos, draw, explain

draw.point(Vector([1, 1, 1]))

θ = Scalar(0)#3.141/2)

rm = Array([[1, 0, 0, 0],
            [0, cos(θ), sin(θ), 0],
            [0, -sin(θ), cos(θ), 0],
            [0, 0, 0, 1]])

explain(rm)

explain(rm@rm)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

m = m @ rm

explain(m)

from eevee import triangles

print(len(triangles))
if 0:#with m:
    for a, b, c, n in triangles[:400]:
        draw.polygon(m@a, m@b, m@c, points=False)

m = Array([[1, 0, 0, 1],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])@m

with m:
    for a, b, c, n in triangles[:400]:
        draw.polygon(a, b, c, points=False, color=draw.red)

draw.point(Vector([1, 1, 1]))

draw.polygon(
    Vector([1, 1, 1]),
    Vector([-1, 1, 1]),
    Vector([-1, -1, 1]),
)
exit()


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

#explain(m)

##draw.labels = False
draw.arrow(Vector([0, 0, 1]), Vector([xy, xy+1, 1]))
draw.point(Vector([1, 0, 1]))

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
for a, b in cube_lines:
    ma = m@a
    draw.line(ma, m@b)
    #explain(ma)

#exit()

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

#explain(point)

#draw.arrow(point, m @ point)

mat = m @ tr
#explain(mat)

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
    draw.point(point, color=draw.gray)
    rotated = mat @ point
    draw.point(rotated)

    #explain(rotated)

#explain(m@m)

#draw(point+point)
m @ m

point = Vector([-2, -8, 2, 1])

#θ = Scalar(3.141/2)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

m @ m
m @ point

#explain(m @ point)

#exit()

print(m @ point)

draw.point(point)
draw.arrow(point, m @ point)
#exit()
draw.polygon(point, m @ point, [-1,5, 0, 1])

#θ = Scalar(3.141/2)
point = Vector([3, 1, 1])

rot = Array([[cos(θ), sin(θ), 0],
             [-sin(θ), cos(θ), 0],
             [0, 0, 1]])

draw.point(rot @ point)

point = Vector([-2, -8, 2, 1])

draw.point(point)

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

draw.labels = False

explain(m)

from eevee import triangles

print(len(triangles))
with m:
    for a, b, c, n in triangles[:400]:
        draw.polygon(a, b, c,points=False)
