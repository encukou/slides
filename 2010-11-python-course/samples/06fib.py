class Fib(object):
    '''An iterator that yields numbers
    in the Fibonacci sequence
    '''

    def __init__(self, max=None):
        self.max = max
        self.a = 0
        self.b = 1

    def next(self):
        fib = self.a
        if self.max and fib > self.max:
            raise StopIteration
        self.a, self.b = self.b, self.a + self.b
        return fib

    def __iter__(self):
        return self
