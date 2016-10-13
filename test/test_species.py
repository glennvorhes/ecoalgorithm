from unittest import TestCase
from ecoalgorithm.models import SpeciesBase
from random import random
from ecoalgorithm.db_connect import db
from ecoalgorithm import models


random_change = 2


class ExampleSpecies(SpeciesBase):

    def __init__(self, x=None, y=None, blue=None):
        self.x = x if type(x) is float else (random() - 0.5) * 200
        self.y = y if type(y) is float else (random() - 0.5) * 200
        self.blue = blue if type(blue) is bool else True if random() >0.5 else False
        super().__init__()

    def mature(self):
        self._success = -1 * (self.x - 15) ** 2 + -1 * (self.y + 4) ** 2 + 25

    def mutate(self):
        pass

    def mate(self, other_individual):
        if random() > 0.5:
            new_x = self.x + (random() - 0.5) * random_change
        else:
            new_x = other_individual.x + (random() - 0.5) * random_change
        if random() > 0.5:
            new_y = self.y + (random() - 0.5) * random_change
        else:
            new_y = other_individual.y + (random() - 0.5) * random_change

        return ExampleSpecies(new_x, new_y)


class SpeciesTest(TestCase):

    # @staticmethod
    # def get_first():
    #     """
    #
    #     :return:
    #     :rtype: models.SpeciesBase
    #     """
    #     return db.sess.query(models.SpeciesBase).first()

    @staticmethod
    def get_by_id(guid):
        """

        :param guid:
        :return:
        :rtype: ExampleSpecies
        """

        g = db.sess.query(models.SpeciesBase).filter(
            models.SpeciesBase._guid == guid
        ).first()
        g.__class__ = ExampleSpecies
        g.__init__()
        return g

    @staticmethod
    def add_one():
        """

        :return:
        :rtype: ExampleSpecies
        """
        ind = ExampleSpecies()
        ind._gen_num = 10

        db.sess.add(ind)
        db.sess.commit()
        return ind

    @staticmethod
    def clear_inds():
        db.sess.query(models.SpeciesBase).delete()
        db.sess.commit()

    def setUp(self):
        pass

    def test_uid(self):
        self.clear_inds()

        ind = ExampleSpecies()
        ind._gen_num = 10
        self.assertIsNone(ind._uid)
        db.sess.add(ind)
        db.sess.commit()

        g = self.get_by_id(ind.guid)
        self.assertIsNotNone(g._uid)

    def test_change_class(self):
        self.clear_inds()

        ind = self.add_one()

        g = self.get_by_id(ind.guid)

        self.assertGreater(len(g.params), 0)
        self.assertGreater(len(g._kwargs), 10)

    def test_repopulate_vals(self):
        self.clear_inds()
        ind = self.add_one()

        x = ind.x
        y = ind.y

        g = self.get_by_id(ind.guid)

        self.assertEqual(g.x, x)
        self.assertEqual(g.y, y)

    def test_mature(self):
        self.clear_inds()
        ind = self.add_one()
        ind.mature()
        db.sess.commit()

    def test_breed(self):
        self.clear_inds()
        total = 2

        ind1 = self.add_one()
        ind2 = self.add_one()
        ind1.mature()
        ind2.mature()
        db.sess.commit()

        out_inds = models._breed(ind1, ind2)
        self.assertEqual(len(out_inds), ind2.get_offspring_count())

        total += ind2.get_offspring_count()

        for f in out_inds:
            f.mature()
            f._gen_num = ind1.gen_num + 1

        db.sess.add_all(out_inds)
        db.sess.commit()

        ind2.set_offspring_count(12)
        total += ind1.get_offspring_count()

        out_inds = models._breed(ind2, ind1)

        for f in out_inds:
            f.mature()
            f._gen_num = ind1.gen_num + 2

        db.sess.add_all(out_inds)
        db.sess.commit()

        self.assertEqual(total, db.sess.query(models.SpeciesBase).count())










