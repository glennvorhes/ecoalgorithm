from unittest import TestCase
from test.test_species import ExampleSpecies
from ecoalgorithm.db_connect import db
from ecoalgorithm import  Ecosystem, SpeciesBase
from ecoalgorithm._models import Generation


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

Cat.validate_class()
Dog.validate_class()
Fish.validate_class()
DeadFish.validate_class()


def species_base_count(gen: Generation) -> int:
    return len([ind for ind in gen.individuals if ind.class_name == SpeciesBase.__name__])


class TestGeneration(TestCase):
    species_set = {Fish, Cat, Dog, DeadFish}

    def setUp(self):
        self.eco = None

    def create_new(self):
        some_inds = [Cat() for i in range(4)]
        some_inds.extend([Dog() for i in range(4)])
        some_inds.extend([Fish() for i in range(4)])
        some_inds.extend([DeadFish() for i in range(4)])
        self._eco = Ecosystem(self.species_set, some_inds, use_existing_results=False)

    @property
    def new_generation(self) -> Generation:
        if self.eco is None:
            self.create_new()
        return self._eco.working_generation

    @property
    def db_generation(self) -> Generation:
        gen = self.new_generation
        gen = db.sess.query(Generation).first()
        return gen


    def test_create_gen(self):
        return
        gen = self.new_generation
        self.assertEqual(species_base_count(gen), 0)

    def test_gen_from_db(self):
        return
        gen = self.db_generation
        self.assertEqual(species_base_count(gen), 0)

    def test_next_gen(self):
        return
        max_pop = 200
        gen = self.db_generation

        with self.assertRaises(AssertionError):
            gen = gen.next_generation

        gen.populate_next_generation(max_pop)
        gen = gen.next_generation

        gen.populate_next_generation(max_pop)
        gen = gen.next_generation

        gen.populate_next_generation(max_pop)
        gen = gen.next_generation

    def test_a_bunch(self):
        max_pop = 20
        gen = self.db_generation

        for i in range(20):
            gen.populate_next_generation(max_pop)
            print(gen.best_success)
            gen = gen.next_generation



