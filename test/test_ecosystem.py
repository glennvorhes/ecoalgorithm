from unittest import TestCase

from test.example_species import Bird, Cat, Fish
from ecoalgorithm.models import DbGeneration
from ecoalgorithm.ecosystem import OneGeneration
from ecoalgorithm.db_connect import db
from ecoalgorithm import models
from ecoalgorithm import Ecosystem


# TODO see what happens if there is only one




max_population = 40
offspring_count = 5
gen_count = 40


class TestEcosystem(TestCase):
    def setUp(self):
        self.inds = []

        Bird.set_offspring_count(7)

        Cat.set_offspring_count(4)

        for i in range(5):
            self.inds.append(Bird())
            self.inds.append(Cat())
            self.inds.append(Fish())

    def tearDown(self):
        pass

    def _delete_db(self):
        pass

    def test_run(self):
        db.clear_db()
        ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(gen_count))

    def test_reinit(self):
        db.clear_db()
        ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(gen_count, 'short'))

        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(gen_count, 'short'))

        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(gen_count, 'short'))

        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(gen_count, 'short'))

    def test_result(self):
        gens = db.sess.query(models.DbGeneration)
        """
        :type: list[models.DbGeneration]
        """

        for g in gens:
            print(g.individuals)
