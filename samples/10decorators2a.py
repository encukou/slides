class Point(list):

    @property
    def x(self):
        return self[0]

    @x.setter
    def x(self, newValue):
        self[0] = newValue

point = Point([1, 2])

assert point.x == 1
point.x = 3
assert point == [3, 2]
