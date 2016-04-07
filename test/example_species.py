__author__ = 'glenn'
from random import random

from eco.species import Individual
from eco.ecosystem import Ecosystem
import numpy as np


class CommonProblem(Individual):
    def __init__(self, x=None, y=None, **kwargs):
        self.x = x or (random() - 0.5) * 200
        self.y = y or (random() - 0.5) * 200
        self.blue = True
        super(CommonProblem, self).__init__(self, *[], **kwargs)

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

            return type(self)(new_x, new_y)


class Cat(CommonProblem):

    def mate(self, other_individual):
            new_x = (random() - 0.5) * random_change + (self.x + other_individual.x) / 2
            new_y = (random() - 0.5) * random_change + (self.y + other_individual.y) / 2

            new_x = -500
            new_y = -500

            return type(self)(new_x, new_y)


class Fish(Cat):
    pass


if __name__ == '__main__':

    inds = []

    for i in range(5):
        inds.append(Bird())
        inds.append(Cat())

    ecosystem = Ecosystem(inds, max_population=100, limit_breeders=30, offspring_count=10,
                          generation_limit=100, use_existing_results=False,
                          print_output=True)
