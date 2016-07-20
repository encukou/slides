database = [
    {'name': 'Petr', 'score': 100},
    {'name': 'Maria', 'score': 300},
    {'name': 'Andy', 'score': 200},
]

# Application

class Player:
    def __init__(self, number):
        self.number = number
        self.name = database[number]['name']
        self.score = database[number]['score']

    @property
    def name(self):
        return database[self.number]['name']

    @name.setter
    def name(self, new_name):
        database[self.number]['name'] = new_name

# Test

def test_everything():
    player = Player(0)
    clone = Player(0)
    assert player.name == 'Petr'
    player.name = 'Peťa'
    assert database[0]['name'] == 'Peťa'
    assert player.name == 'Peťa'
    assert clone.name == 'Peťa'
