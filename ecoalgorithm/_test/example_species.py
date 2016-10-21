from random import random
from ecoalgorithm import SpeciesBase

from time import sleep


_random_change = 2


class ExampleSpecies(SpeciesBase):
    def __init__(self, x=None, y=None, blue=None, null_val=None):
        self.x = x if type(x) is float else (random() - 0.5) * 200
        self.y = y if type(y) is float else (random() - 0.5) * 200
        self.blue = blue if type(blue) is bool else True if random() > 0.5 else False
        self.null_val = null_val
        super().__init__()

    def mature(self):
        # dummy processing
        #
        dummy = 0
        for i in range(100000):
            dummy += 0.1

        # sleep(1)
        self.success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25

    def mutate(self):
        pass

    def mate(self, other_individual):
        if random() > 0.5:
            new_x = self.x + (random() - 0.5) * _random_change
        else:
            new_x = other_individual.x + (random() - 0.5) * _random_change
        if random() > 0.5:
            new_y = self.y + (random() - 0.5) * _random_change
        else:
            new_y = other_individual.y + (random() - 0.5) * _random_change

        return self.__class__(new_x, new_y)


class Cat(ExampleSpecies):
    pass


class Dog(ExampleSpecies):
    pass


class Fish(ExampleSpecies):
    pass


class DeadFish(ExampleSpecies):

    def mature(self):
        self.success = None


class Snake(ExampleSpecies):
    pass


class Racoon(ExampleSpecies):

    def mature(self):
        pass



def get_some_inds():

    some_individuals = []

    for i in range(4):
        some_individuals.append(Cat())
        some_individuals.append(Dog())
        some_individuals.append(Fish())
        some_individuals.append(DeadFish())

    return some_individuals


def get_some_inds_len():
    return len(get_some_inds())


def get_species_set():
    species_set = {Fish, Cat, Dog, DeadFish}

    Fish._validated = False
    Cat._validated = False
    Dog._validated = False
    DeadFish._validated = False
    return species_set


__all__ = [get_species_set, get_some_inds, get_some_inds_len, Dog, Cat, Fish, DeadFish, ExampleSpecies]
