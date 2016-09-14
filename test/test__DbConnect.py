from unittest import TestCase
from ecoalgorithm.db_connect import db
from ecoalgorithm import models
import ecoalgorithm

ecoalgorithm.config.db_path = '/home/glenn/PycharmProjects/ecoalgorithm/ecoalgorithm/results4.db'


class TestDbConnect(TestCase):
    def setUp(self):
        self.db = db
        self.db.clear_db()

    def tearDown(self):
        self.db.delete_db()

    def test_engine(self):
        self.assertIsNot(self.db.engine, None)

    def test_sess(self):
        self.assertIsNot(self.db.sess, None)

    def test_close_connection(self):
        self.db.close_connection()
        self.db.sess.query(models.DbGeneration)

    def test_clear_db(self):
        models.DbGeneration([])
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 1)

        self.db.clear_db()
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 0)

    def test_delete_db(self):
        models.DbGeneration([])
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 1)

        self.db.delete_db()
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 0)

    def test_is_same(self):
        db1 = self.db.sess
        db2 = self.db.sess
        self.assertIs(db1, db2)

        self.db.close_connection()

        db3 = self.db.sess
        self.assertIsNot(db1, db3)

    def test_change_db(self):
        models.DbGeneration([])
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 1)

        ecoalgorithm.config.db_path = '/home/glenn/PycharmProjects/ecoalgorithm/ecoalgorithm/results10.db'
        models.DbGeneration([])
        g = self.db.sess.query(models.DbGeneration).all()
        self.assertEqual(len(g), 1)

        with self.assertRaises(AssertionError):
            ecoalgorithm.config.db_path = '/home/glenn/PycharmProjects/ecoalgorithm/ecoalgorithm/results10.dbb'




