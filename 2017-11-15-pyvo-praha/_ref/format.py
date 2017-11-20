barva = 'zelená'
pocet = 17

msg = 'Louka je {barva} a pase se na ní {pocet} telátek'

print(msg.format(barva=barva, pocet=pocet))

params = dict(
    barva = 'zelená',
    pocet = 17,
)

print(msg.format(**params))

class ParamDict(dict):
    def __missing__(self, key):
        return '<{}>'.format(key)

params = ParamDict(barva='zelená')

print(msg.format_map(params))

print(f'Louka je {barva} a pase se na ní {pocet} telátek')
