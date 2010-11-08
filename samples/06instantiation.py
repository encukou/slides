class ExampleClass(object):
    a, b, c = 1, 2, 3

exampleInstance = ExampleClass()

exampleInstance.a = 10

assert exampleInstance.a == 10
assert exampleInstance.b == 2

assert exampleClass.a == 1
