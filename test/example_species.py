__author__ = 'glenn'
import test
from random import random

from ecoalgorithm.species import SpeciesBase
from ecoalgorithm.ecosystem import Ecosystem
import numpy as np
from datetime import datetime

class CommonProblem(SpeciesBase):
    def __init__(self, success=None, **kwargs):
        self.x = None
        self.y = None
        self.blue = None

        kwargs['x'] = (random() - 0.5) * 200 if 'x' not in kwargs else kwargs['x']
        kwargs['y'] = (random() - 0.5) * 200 if 'y' not in kwargs else kwargs['y']
        kwargs['blue'] = True

        super(CommonProblem, self).__init__(success, **kwargs)

    def mature(self):
        self._success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25
        # self.die()

random_change = 2


class Bird(CommonProblem):

    def mate(self, other_individual):
            if random() > 0.5:
                new_x = self.x + (random() - 0.5) * random_change
            else:
                new_x = other_individual.x + (random() - 0.5) * random_change
            if random() > 0.5:
                new_y = self.y + (random() - 0.5) * random_change
            else:
                new_y = other_individual.y + (random() - 0.5) * random_change

            return type(self)(**{'x': new_x, 'y': new_y})


class Cat(CommonProblem):

    def mate(self, other_individual):
            new_x = (random() - 0.5) * 2 + (self.x + other_individual.x) / 2
            new_y = (random() - 0.5) * 2 + (self.y + other_individual.y) / 2

            # new_x = -500
            # new_y = -500

            return type(self)(**{'x': new_x, 'y': new_y})

    def mature(self):
        super().mature()
        if random() > 0.5:
            self.die()
        # print('dead Cat')



class Fish(CommonProblem):
    def mate(self, other_individual):
            new_x = (random() - 0.5) * 10 + (self.x + other_individual.x) / 2
            new_y = (random() - 0.5) * 10 + (self.y + other_individual.y) / 2

            # new_x = 500
            # new_y = 500

            return type(self)(**{'x': new_x, 'y': new_y})


class NewSpecies(SpeciesBase):

    def __init__(self, success=None, **kwargs):
        self.bird = None
        self.cat = None
        self._fish = None
        self._car = "can"

        if len(kwargs) == 0:
            kwargs['bird'] = 5
            kwargs['cat'] = 10

        super().__init__(success, **kwargs)

    def mature(self):
        self._success = 10

    def mate(self, other_individual):
        return NewSpecies()


if __name__ == '__main__':
    NewSpecies.validate_species()

