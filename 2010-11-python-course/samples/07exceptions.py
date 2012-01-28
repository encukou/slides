def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print "Division by zero!"
    except TypeError as e:
        print "Type error:", e
    except Exception:
        print "Unknown error occured!"
    else:
        print "The answer is %s." % result