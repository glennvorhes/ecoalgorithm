from unittest import TestCase
from test.example_species import Bird, Cat, Fish
from ecoalgorithm.models import DbGeneration
from ecoalgorithm.ecosystem import OneGeneration
from ecoalgorithm import db_connect
from ecoalgorithm import models

db_conn = db_connect.db


class TestOneGeneration(TestCase):
    def setUp(self):
        self.inds = []

        Bird.set_offspring_count(7)

        Cat.set_offspring_count(4)

        for i in range(5):
            self.inds.append(Bird())
            self.inds.append(Cat())
            self.inds.append(Fish())

        self.input_pop_len = len(self.inds)

    def tearDown(self):
        pass

    def test_create_gen(self):
        gen = OneGeneration(self.inds)
        self.assertIsInstance(gen, OneGeneration)

    def test_mature(self):
        gen = OneGeneration(self.inds)
        gen.mature()

    def test_breed(self):
        max_pop = 50
        gen = OneGeneration(self.inds, max_population=max_pop)
        gen.mature()
        gen.breed()
        self.assertEqual(len(gen.next_gen_individuals), max_pop)

    def test_print_stats(self):
        max_pop = 50
        gen = OneGeneration(self.inds, max_population=max_pop)
        gen.mature()
        gen.breed()
        # gen.print_stats()
        self.assertEqual(len(gen.next_gen_individuals), max_pop)

    def test_write_to_db(self):
        max_pop = 50
        gen = OneGeneration(self.inds, max_population=max_pop)
        gen.mature()
        gen.breed()
        self.assertEqual(len(gen.next_gen_individuals), max_pop)

        db_conn.sess.query(models.DbGeneration).delete()
        db_conn.sess.query(models.DbIndividual).delete()
        db_conn.sess.commit()

        gen.write_to_db()

        g = db_conn.sess.query(models.DbGeneration).filter(models.DbGeneration.gen_num == 1).first()
        """
        :type: models.DbGeneration
        """

        self.assertIsNotNone(g, 'DbGeneration should not be none')

        self.assertEqual(self.input_pop_len, len(g.individuals),
                         'length of individuals and in db should be same')

        # def test_setup2(self):
        #     print('test2')
