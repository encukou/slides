def log(message):
    with open("file.log") as f:
        f.write(message)

v = 'three'

try:
    int(v)
except ValueError as err:
    log("could not convert value")
    raise err
