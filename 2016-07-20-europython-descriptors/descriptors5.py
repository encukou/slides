database = [
    {'name': 'Petr', 'score': 100},
    {'name': 'Maria', 'score': 300},
    {'name': 'Andy', 'score': 200},
]

# Framework/Library

def fix_model(cls):
    for attrname in dir(cls):
        attr = getattr(cls, attrname)
        if isinstance(attr, Column):
            attr.name = attrname

class Column:
    def __get__(self, instance, owner_class):
        if instance is None:
            return self
        else:
            return database[instance.number][self.name]

    def __set__(self, instance, new_value):
        database[instance.number][self.name] = new_value

# Application

class Player:
    def __init__(self, number):
        self.number = number

    name = Column()
    score = Column()


fix_model(Player)

# Test

def test_everything():
    player = Player(0)
    clone = Player(0)
    assert player.name == 'Petr'
    player.name = 'Peťa'
    assert database[0]['name'] == 'Peťa'
    assert player.name == 'Peťa'
    assert clone.name == 'Peťa'
