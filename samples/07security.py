def secure_open(filename):
    if filename == '/etc/passwd':
        raise IOError('Access denied')
    else:
        return open(filename)
