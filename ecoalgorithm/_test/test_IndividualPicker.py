import ecoalgorithm
from .example_species import get_some_inds, Cat, get_species_set
from unittest import TestCase
from .._helpers import IndividualPicker, mature_all, printd
from typing import List


def get_some_cats() -> List[ecoalgorithm.SpeciesBase]:
    out_inds = []

    for i in range(50):
        out_inds.append(Cat())

    return out_inds


def get_some_cats_mature() -> List[ecoalgorithm.SpeciesBase]:
    out_inds = get_some_cats()
    ecoalgorithm.config.multithread = False
    mature_all(out_inds)
    return out_inds


def initialize_sucess():
    eco = ecoalgorithm.Ecosystem(get_species_set(), get_some_inds(), use_existing=False)

    eco.run(200, ecoalgorithm.ShowOutput.SHORT)


class TestIndividualPicker(TestCase):
    def test_population_pick(self):
        pass

        # initialize_sucess()

        picker = IndividualPicker(get_some_cats_mature())

        ecoalgorithm.config.picker_weight = 2

        for i in range(30):
            fem = picker.pick_female()
            picker.pick_male(fem)

        print(picker.summary_str)

    def test_multithread(self):
        ecoalgorithm.config.multithread = True
        inds = get_some_cats()
        mature_all(inds)

        for ind in inds:
            self.assertTrue(ind.is_mature)

    def test_singletrhead(self):
        ecoalgorithm.config.multithread = False
        inds = get_some_cats()
        mature_all(inds)
        for ind in inds:
            self.assertTrue(ind.is_mature)
