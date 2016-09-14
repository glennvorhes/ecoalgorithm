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

    def _clear_db(self):
        pass
        #
        # db.sess.query(models.DbIndividual).delete()
        # db.sess.
        # db.sess.query(models.DbGeneration).delete()
        # models.

    def _delete_db(self):
        pass

    def test_reinitialize_eco(self):
        self.ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat], use_existing_results=True,
                                   max_population=max_population, picker_power=2)

