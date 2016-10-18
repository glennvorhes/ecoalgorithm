from ecoalgorithm import db
from .. import Ecosystem, SpeciesBase
from .._models import Generation
from .example_species import Cat, Dog, Fish, DeadFish, get_some_inds, get_species_set
from unittest import TestCase


Cat.validate_class()
Dog.validate_class()
Fish.validate_class()
DeadFish.validate_class()


def species_base_count(gen: Generation) -> int:
    return len([ind for ind in gen.individuals if ind.class_name == SpeciesBase.__name__])


class TestGeneration(TestCase):
    # species_set = {Fish, Cat, Dog, DeadFish}

    def setUp(self):
        db.clear_db()
        self.eco = None

    def create_new(self):

        self._eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)

    def make_new_generation(self) -> Generation:
        if self.eco is None:
            self.create_new()
        return self._eco.working_generation

    @property
    def new_generation(self) -> Generation:
        return self.make_new_generation()

    @property
    def db_generation(self) -> Generation:
        self.make_new_generation()
        gen = db.sess.query(Generation).first()
        return gen

    def test_create_gen(self):
        gen = self.new_generation
        self.assertEqual(species_base_count(gen), 0)

    def test_gen_from_db(self):
        gen = self.db_generation
        self.assertEqual(species_base_count(gen), 0)

    def test_next_gen(self):
        max_pop = 200
        keep_all = True
        gen = self.db_generation

        with self.assertRaises(AssertionError):
            gen = gen.next_generation

        gen.populate_next_generation(max_pop, keep_all)
        gen = gen.next_generation

        gen.populate_next_generation(max_pop, keep_all)
        gen = gen.next_generation

        gen.populate_next_generation(max_pop, keep_all)
        gen = gen.next_generation
        self.assertIsNotNone(gen.gen_num)

    def test_a_bunch(self):
        max_pop = 20
        keep_all = True
        gen = self.db_generation

        for i in range(20):
            gen.populate_next_generation(max_pop, keep_all)
            # print(gen.best_success)
            gen = gen.next_generation
