info(obj)
info(obj, 20)
info(obj, 20, True)
info(obj, 20, collapse=True)
info(obj, spacing=20, collapse=True)
info(obj, collapse=True)
info(collapse=True, object=obj)

arguments = [obj, 20]
info(*arguments)

kwargs = dict(collapse=True, spacing=20)
info(obj, **kwargs)

def countargs(*args):
    print "Got %s arguments." % len(args)

countargs(1, 2, 3)