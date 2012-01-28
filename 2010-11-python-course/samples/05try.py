try:
    result = a / b
except ZeroDivisionError:
    print "b may not be zero!"
except Exception:
    print "An unexpected error occured!"
else:
    print "All is good; result =", result
finally:
    print "This line executes in any case"