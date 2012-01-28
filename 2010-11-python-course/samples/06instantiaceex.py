class ExampleClass(object):
    a, b, c = 1, 2, 3

exampleInstance = ExampleClass()

exampleInstance.a = exampleInstance.a + 1

assert exampleInstance.a == 2

assert exampleClass.a == 1
