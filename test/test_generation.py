from unittest import TestCase
from test.test_species import ExampleSpecies
from ecoalgorithm import models
from ecoalgorithm.db_connect import db
from ecoalgorithm.ecosystem import Ecosystem


class Cat(ExampleSpecies):
    pass


class Dog(ExampleSpecies):
    pass


class Fish(ExampleSpecies):
    pass


class DeadFish(ExampleSpecies):
    def mature(self):
        self.success = None

species_set = {Fish, Cat, Dog, DeadFish}

class TestGeneration(TestCase):
    def clear_db(self):
        db.sess.query(models.Generation).delete()
        db.sess.query(models.SpeciesBase).delete()
        db.sess.commit()

    def make_dummy_generation(self):
        self.clear_db()

        gen = models.Generation()

        some_inds = [Cat() for i in range(4)]
        some_inds.extend([Dog() for i in range(4)])
        some_inds.extend([Fish() for i in range(8)])
        some_inds.extend([DeadFish() for i in range(4)])

        # gen.individuals.extend(some_inds)

        gen.add_individuals(some_inds)

        gen.save()


    def test_create_gen(self):
        return
        self.make_dummy_generation()

    def test_recover_gen(self):
        return
        gen = db.sess.query(models.Generation).first()

        """
        :type: models.Generation
        """

        gen.fix_species_classes(species_set)

        # print(gen.best_success)

        # print(gen.individuals)

    def test_make_ecosystem(self):

        eco = Ecosystem(species_set, max_population=20)
        print(eco._working_generation.best_success)

        gen = eco._working_generation

        print(gen._next_generation)


        # print(eco)



