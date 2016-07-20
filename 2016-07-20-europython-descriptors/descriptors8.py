database = [
    {'name': 'Petr', 'score': 100},
    {'name': 'Maria', 'score': 300},
    {'name': 'Andy', 'score': 200},
]

# Framework/Library

global_counter = 0

class Column:
    def __init__(self):
        global global_counter
        self.counter = global_counter
        global_counter += 1

    def __set_name__(self, owner_class, name):
        self.name = name

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

# Test

def test_everything():
    player = Player(0)
    clone = Player(0)
    assert player.name == 'Petr'
    player.name = 'Peťa'
    assert database[0]['name'] == 'Peťa'
    assert player.name == 'Peťa'
    assert clone.name == 'Peťa'

def test_attribute_order():
    assert Player.name.counter < Player.score.counter
