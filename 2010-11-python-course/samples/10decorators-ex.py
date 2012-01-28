@decorator
def function():
    return 1

###

def function():
    return 1
function = decorator(function)
