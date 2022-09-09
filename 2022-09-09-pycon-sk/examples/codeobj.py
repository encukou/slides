code = compile('1 + 2', 'expression.py', 'eval')

for name in dir(code):
    if not name.startswith('_'):
        print(name, getattr(code, name))
