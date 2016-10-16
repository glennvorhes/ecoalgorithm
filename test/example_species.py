from random import random
from ecoalgorithm import SpeciesBase


random_change = 2


class ExampleSpecies(SpeciesBase):
    def __init__(self, x=None, y=None, blue=None):
        self.x = x if type(x) is float else (random() - 0.5) * 200
        self.y = y if type(y) is float else (random() - 0.5) * 200
        self.blue = blue if type(blue) is bool else True if random() > 0.5 else False
        super().__init__()

    def mature(self):
        self.success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25

    def mutate(self):
        pass

    def mate(self, other_individual):
        if random() > 0.5:
            new_x = self.x + (random() - 0.5) * random_change
        else:
            new_x = other_individual.x + (random() - 0.5) * random_change
        if random() > 0.5:
            new_y = self.y + (random() - 0.5) * random_change
        else:
            new_y = other_individual.y + (random() - 0.5) * random_change

        return self.__class__(new_x, new_y)



class Cat(ExampleSpecies):
    pass
    # def __init__(self):
    #     super().__init__()


class Dog(ExampleSpecies):
    pass
    # def __init__(self):
    #     super().__init__()


class Fish(ExampleSpecies):
    pass
    # def __init__(self):
    #     super().__init__()


class DeadFish(ExampleSpecies):

    # def __init__(self):
    #     super().__init__()

    def mature(self):
        self.success = None
