from ecoalgorithm import db, config
from .. import Ecosystem, SpeciesBase
from .example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, \
    get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies
from unittest import TestCase
from typing import List
from .. import ShowOutput
import os


def get_eco_inds(eco: Ecosystem) -> List[SpeciesBase]:
    return eco._working_generation.individuals


def get_eco_inds_len(eco: Ecosystem) -> int:
    return len(get_eco_inds(eco))


def build_example():
    db.clear_db()
    config.multithread = False
    eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
    eco.run(100, ShowOutput.SHORT)


class TestEcosystem(TestCase):
    
    def setUp(self):
        config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'eco.db')

    def test_create_no_existing(self):
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        self.assertEqual(get_eco_inds_len(eco), get_some_inds_len())

    def test_class_validation(self):
        db.clear_db()
        with self.assertRaises(AssertionError):
            Ecosystem({Snake, Fish, Racoon})

    def test_recover_existing(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        self.assertEqual(get_eco_inds_len(eco), get_some_inds_len())
        eco = Ecosystem(get_species_set())
        self.assertEqual(get_eco_inds_len(eco), get_some_inds_len())
        eco = Ecosystem(get_species_set(), [Cat(), Cat()])
        self.assertEqual(get_eco_inds_len(eco), get_some_inds_len() + 2)

    def test_add_not_in_set(self):
        config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'not_in_set.db')
        db.clear_db()
        inds = get_some_inds()
        inds.append(Snake())
        inds.append(Snake())
        inds.append(Snake())
        inds.append(Snake())
        eco = Ecosystem(get_species_set(), inds, use_existing=False)
        eco.run(1)

        with self.assertRaises(KeyError):
            Ecosystem(get_species_set())

        Ecosystem(get_species_set(), [Snake(), Snake()])

    def test_add_empty(self):
        # return
        Ecosystem(get_species_set(), [Snake()], use_existing=False)

    def test_add_empty_no_ind(self):
        # return
        with self.assertRaises(AssertionError):
            Ecosystem(get_species_set(), [], use_existing=False)

    def test_thinks_existing(self):
        # return
        with self.assertRaises(AssertionError):
            Ecosystem(get_species_set(), use_existing=False)

        Ecosystem(get_species_set(), [Snake()])
        db.clear_db()
        Ecosystem(get_species_set(), get_some_inds(), use_existing=True)

    def test_start_run(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        eco.run(5)
        eco = Ecosystem(get_species_set())
        eco.run(5)

    def test_keep_all(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        eco.run(2)
        inds = get_eco_inds(eco)
        dead_fish = [ind for ind in inds if type(ind) is DeadFish]
        self.assertEqual(len(dead_fish), DeadFish.get_offspring_count())

    def test_not_keep_all(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, keep_all=False)
        eco.run(2)
        inds = get_eco_inds(eco)
        dead_fish = [ind for ind in inds if type(ind) is DeadFish]
        self.assertEqual(len(dead_fish), 0)

    def test_keep_all_all_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish(), DeadFish()], use_existing=False)
        eco.run(3)
        inds = get_eco_inds(eco)
        print(inds)

    def test_not_keep_all_all_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish(), DeadFish()], use_existing=False, keep_all=False)
        eco.run(3)
        # inds = get_eco_inds(eco)

    def test_show_output(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)

        eco.run(3, ShowOutput.SHORT)
        eco.run(3, ShowOutput.LONG)

    def test_bail_on_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish()], use_existing=False)
        eco.run(20)

    def test_threshold(self):
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        eco.run(100, ShowOutput.SHORT, break_threshold=1)

    def test_min_max_population(self):
        with self.assertRaises(AssertionError):
            eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=10)

