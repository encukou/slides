class A(object):

    @classmethod
    def classId(cls):
        return cls.__name__

class B(A):
    pass

aInstance = A()
bInstance = B()

assert A.classId() == "A"
assert B.classId() == "B"
assert aInstance.classId() == "A"
assert bInstance.classId() == "B"

