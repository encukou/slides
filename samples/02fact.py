def factorial(n):
    """Compute the factorial of n, printing progress"""
    print 'n =', n
    if n > 1:
        return n * factorial(n - 1)
    else:
        print "The end"
        return 1

print factorial(5)
