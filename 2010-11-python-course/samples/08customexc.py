class SecurityError(IOError):
    pass

def secure_open(filename):
    if filename == '/etc/passwd':
        raise SecurityError('Access denied')
    else:
        return open(filename)
