import random

class Player:
    """ Initialze Player.
    """
    def __init__(self, id):
        self.id = id
        self.hp = 10
        self.state = True
        self.current_comment = None


    def attack(self, value):
        int_value = int(value)
        attacked_value = abs(int_value - random.randint(0, 9))
        return attacked_value

    def defend(self, value):
        int_value = int(value)
        defend_value = abs(int_value - random.randint(0, 9))
        self.hp += abs(defend_value)
        if self.hp < 1:
            self.state = False
        return defend_value
