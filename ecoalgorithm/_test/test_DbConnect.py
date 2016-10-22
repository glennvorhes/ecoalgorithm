from unittest import TestCase
from ecoalgorithm import db
import ecoalgorithm
from .. import _models as models
import os
from .example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, \
    get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies

ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'conn_test.db')


class TestDbConnect(TestCase):
    def setUp(self):
        db.clear_db()

    def tearDown(self):
        pass

    def test_engine(self):
        self.assertIsNotNone(db.engine)

    def test_sess(self):
        self.assertIsNotNone(db.sess)

    def test_close_connection(self):
        db.close_connection()
        db.sess.query(models.Generation)

    def test_clear_db(self):
        g = db.sess.query(models.Generation).all()
        self.assertEqual(len(g), 0)

        db.clear_db()
        g = db.sess.query(models.Generation).all()
        self.assertEqual(len(g), 0)

    def test_delete_db(self):
        gen = models.Generation(get_species_set())
        gen.add_individuals(get_some_inds())
        gen.save()
        g = db.sess.query(models.Generation).all()
        self.assertEqual(len(g), 1)

        db.delete_db()
        g = db.sess.query(models.Generation).all()
        self.assertEqual(len(g), 0)

    def test_is_same(self):
        db1 = db.sess
        db2 = db.sess
        self.assertIs(db1, db2)

        db.close_connection()

        db3 = db.sess
        self.assertIsNot(db1, db3)

    def test_change_db(self):
        ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'db2.db')
        db.clear_db()
        gen = models.Generation(get_species_set())
        gen.add_individuals(get_some_inds())
        gen.save()
        g = db.sess.query(models.Generation).count()
        self.assertEqual(g, 1)

        ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'db3.db')
        db.clear_db()
        gen = models.Generation(get_species_set())
        gen.add_individuals(get_some_inds())
        gen.save()
        g = db.sess.query(models.Generation).count()
        self.assertEqual(g, 1)

        ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'db2.db')
        g = db.sess.query(models.Generation).count()
        self.assertEqual(g, 1)

        with self.assertRaises(AssertionError):
            ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'cats', 'db.db')

        with self.assertRaises(AssertionError):
            ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'db.dbbbbb')


