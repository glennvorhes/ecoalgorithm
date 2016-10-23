from .example_species import ExampleSpecies, get_species_lookup
from unittest import TestCase
from ecoalgorithm import db, SpeciesBase, config
from .. import _helpers
import os
from .._helpers import printd



class SpeciesTest(TestCase):

    @staticmethod
    def get_by_id(guid):
        """

        :param guid:
        :return:
        :rtype: ExampleSpecies
        """

        return ExampleSpecies.get_by_guid(guid)

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
        db.sess.query(SpeciesBase).delete()
        db.sess.commit()

    def setUp(self):
        config.db_path = os.path.join(os.path.dirname(__file__), 'test_dbs', 'species.db')

    def test_uid(self):
        self.clear_inds()

        ind = ExampleSpecies()

        ind._gen_num = 10
        self.assertFalse(ind.is_in_db)
        db.sess.add(ind)
        db.sess.commit()

        g = self.get_by_id(ind.guid)
        self.assertTrue(g.is_in_db)

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

        out_inds = _helpers.breed(ind1, ind2)
        self.assertEqual(len(out_inds), ind2.get_offspring_count())

        total += ind2.get_offspring_count()

        for f in out_inds:
            f.mature()
            f._gen_num = ind1.gen_num + 1

        db.sess.add_all(out_inds)
        db.sess.commit()

        ind2.set_offspring_count(12)
        total += ind1.get_offspring_count()

        out_inds = _helpers.breed(ind2, ind1)

        for f in out_inds:
            f.mature()
            f._gen_num = ind1.gen_num + 2

        db.sess.add_all(out_inds)
        db.sess.commit()

        self.assertEqual(total, db.sess.query(SpeciesBase).count())

    def test_breed_assertions(self):
        self.clear_inds()

        ind1 = self.add_one()
        ind2 = self.add_one()
        with self.assertRaises(AssertionError):
            _helpers.breed(ind1, ind2)

        ind1.mature()
        ind2.mature()

        _helpers.breed(ind1, ind2)

        ind1.success = None
        with self.assertRaises(AssertionError):
            _helpers.breed(ind1, ind2)

        ind1.success = 10
        _helpers.breed(ind1, ind2)

    def test_validate_class(self):
        self.assertTrue(ExampleSpecies.validate_class())

    def test_get_parents(self):
        self.clear_inds()

        ind1 = self.add_one()
        ind2 = self.add_one()

        x = ind1.x
        y = ind2.y

        ind1.mature()
        ind2.mature()

        out_list = _helpers.breed(ind1, ind2)

        for o in out_list:
            o._gen_num = 10

        db.sess.add_all(out_list)
        db.sess.commit()

        moth =out_list[0].mother
        fath = out_list[0].father

        lkp = get_species_lookup()
        moth.__class__ = lkp[moth._class_name]
        fath.__class__ = lkp[fath._class_name]
        moth.__init__()
        fath.__init__()

        self.assertEquals(x, moth.x)
        self.assertEquals(y, fath.y)

        out_list[0]._mother_id = None

        self.assertIsNone(out_list[0].mother)
