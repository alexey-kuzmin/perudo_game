from random2 import choice

NOMINAL_DICE = [str(i) for i in range(1, 6)] + ['*']


class HandDice:

    def __init__(self, number_of_dice=5, hand_dice=None):
        """Создаем случайную руку"""
        if hand_dice is None:
            self.hand_dice = '*' * number_of_dice
        else:
            self.hand_dice = hand_dice
        self.number_of_dice = len(self.hand_dice)

    def __add__(self, other):
        """ + возвращает новый объект класса"""
        number_of_dice = self.number_of_dice + other.number_of_dice
        hand_dice = self.hand_dice + other.hand_dice
        return HandDice(number_of_dice, hand_dice)

    def get_number_of_dice(self):
        return self.number_of_dice

    def get_hand_dice(self):
        return self.hand_dice

    def del_dice(self):
        """Удалить 1 кубик из руки (пока один)"""
        self.number_of_dice -= 1

    def new_dice_roll(self):
        """Новый бросок кубиков"""
        self.hand_dice = ''.join([choice(NOMINAL_DICE) for _ in range(self.number_of_dice)])

    def check_dice(self, values):
        return self.hand_dice.count(values) + self.hand_dice.count('*')


if __name__ == '__main__':
    a = HandDice()
    b = HandDice()
    a.new_dice_roll()
    b.new_dice_roll()
    print(a.get_hand_dice())
    # print(a.get_hand_dice(), b.hand_dice)
    # c = a + b
    # print(c.hand_dice)
    # print(c.check_dice(4))
