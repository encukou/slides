def info(object, spacing=10, collapse=True):
    """Print method names and their docstrings.

    Takes any object
    spacing: size of the column reserved for names
    collapse: if true, the docstring will be collapsed to a single line
    """
    attrList = [name for name in dir(object) if not name.startswith('_')]

    if collapse:
        processFunc = lambda s: " ".join(s.split())
    else:
        processFunc = lambda s: s

    for attrName in attrList:
        method = getattr(object, attrName)
        if callable(method):
            print attrName.ljust(spacing), processFunc(str(method.__doc__))

if __name__ == "__main__":
    print info.__doc__
