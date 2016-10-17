from ecoalgorithm.db_connect import db
from .. import Ecosystem, SpeciesBase
from .example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies
from unittest import TestCase
from typing import List
from .. import ShowOutput


def get_eco_inds(eco: Ecosystem) -> List[SpeciesBase]:
    return eco._working_generation.individuals


def get_eco_inds_len(eco: Ecosystem) -> int:
    return len(get_eco_inds(eco))


def build_example():
    eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=50)
    eco.run(3, ShowOutput.SHORT)


class TestEcosystem(TestCase):


    def test_create_no_existing(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        self.assertEqual(get_eco_inds_len(eco), get_some_inds_len())

    def test_class_validation(self):
        # return
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
        # return
        inds = get_some_inds()
        inds.append(Snake())
        inds.append(Snake())
        inds.append(Snake())
        inds.append(Snake())
        Ecosystem(get_species_set(), inds, use_existing=False)

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
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=20)
        eco.run(5)
        eco = Ecosystem(get_species_set(), max_population=20)
        eco.run(5)

    def test_keep_all(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=20, )
        eco.run(2)
        inds = get_eco_inds(eco)
        dead_fish = [ind for ind in inds if type(ind) is DeadFish]
        self.assertEqual(len(dead_fish), DeadFish.get_offspring_count())

    def test_not_keep_all(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=20, keep_all=False)
        eco.run(2)
        inds = get_eco_inds(eco)
        dead_fish = [ind for ind in inds if type(ind) is DeadFish]
        self.assertEqual(len(dead_fish), 0)

    def test_keep_all_all_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish(), DeadFish()], use_existing=False, max_population=20, )
        eco.run(3)
        inds = get_eco_inds(eco)
        print(inds)

    def test_not_keep_all_all_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish(), DeadFish()], use_existing=False, max_population=20, keep_all=False)
        eco.run(3)
        # inds = get_eco_inds(eco)

    def test_show_output(self):
        # return
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=20)

        eco.run(3, ShowOutput.SHORT)
        eco.run(3, ShowOutput.LONG)

    def test_bail_on_dead(self):
        # return
        eco = Ecosystem({DeadFish}, [DeadFish()], use_existing=False, max_population=20)
        eco.run(20)

    def test_threshold(self):
        eco = Ecosystem(get_species_set(), get_some_inds(), use_existing=False, max_population=50)
        eco.run(100, ShowOutput.SHORT, break_threshold=1)
