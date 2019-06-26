from presentation import Array, Vector, Scalar, sin, cos, draw

xy = Scalar(0.0)

m = Array([[1, 0, xy],
           [1, 2, xy],
           [0, 0, 1]])

point = Vector([3, xy+1, 1])

draw.arrow(point, m @ m @ point)
#draw(point+point)
exit()
m @ m

point = Vector([-2, -8, 2, 1])

θ = Scalar(3.141/2)

m = Array([[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]])

m @ m
m @ point

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
