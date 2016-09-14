__author__ = 'glenn'
from random import random

from ecoalgorithm.species import Individual
from ecoalgorithm.ecosystem import Ecosystem
import numpy as np


class CommonProblem(Individual):
    def __init__(self, success=None, **kwargs):
        self.x = None
        self.y = None
        self.blue = None

        kwargs['x'] = (random() - 0.5) * 200 if 'x' not in kwargs else kwargs['x']
        kwargs['y'] = (random() - 0.5) * 200 if 'y' not in kwargs else kwargs['y']
        kwargs['blue'] = True

        super(CommonProblem, self).__init__(success, **kwargs)

    def mature(self):
        self.success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25

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
            new_x = (random() - 0.5) * random_change + (self.x + other_individual.x) / 2
            new_y = (random() - 0.5) * random_change + (self.y + other_individual.y) / 2

            new_x = -500
            new_y = -500

            return type(self)(**{'x': new_x, 'y': new_y})


class Fish(Cat):
    pass


if __name__ == '__main__':
    pass
