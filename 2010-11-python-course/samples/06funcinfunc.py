def make_adder(x):
    def adder(y):
        return x + y
    return adder

add2 = make_adder(2)

assert add2(3) == 5
