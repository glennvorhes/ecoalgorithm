import ecoalgorithm
ecoalgorithm.config.db_path = '/home/glenn/PycharmProjects/ecoalgorithm/results.db'

from unittest import TestCase


from ecoalgorithm.ecosystem import Ecosystem
from test.example_species import Bird, Cat, Fish
from ecoalgorithm import models
from ecoalgorithm.db_connect import db

from ecoalgorithm.models import DbGeneration


max_population = 40
offspring_count = 5


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

    # def test_run(self):
    #     db.clear_db()
    #     ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat, Fish], use_existing_results=True,
    #                           max_population=max_population, picker_power=2)
    #
    #     print(ecosystem.run(100))

    def test_reinit(self):
        db.clear_db()
        ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(100, 'short'))

        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(100, 'short'))


        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(100, 'short'))
        #
        ecosystem = Ecosystem(species_classes=[Bird, Cat, Fish], use_existing_results=True,
                              max_population=max_population, picker_power=2)

        print(ecosystem.run(100, 'short'))
