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

    def set_name(self, name):
        self.name = name
        database[self.number]['name'] = name

# Test

def test_everything():
    player = Player(0)
    assert player.name == 'Petr'
    player.set_name('Peťa')
    assert database[0]['name'] == 'Peťa'
    assert player.name == 'Peťa'
    # clone?
