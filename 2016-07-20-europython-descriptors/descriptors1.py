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

# Test

def test_everything():
    assert Player(0).name == 'Petr'
    assert Player(1).score == 300
