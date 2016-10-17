from .example_species import get_some_inds, Cat, get_species_set
from unittest import TestCase
import ecoalgorithm
from .._helpers import IndividualPicker, mature_all


def get_some_cats():
    out_inds = []

    for i in range(50):
        out_inds.append(Cat())

    mature_all(out_inds)

    return out_inds


def initialize_sucess():
    eco = ecoalgorithm.Ecosystem(get_species_set(), get_some_inds(), use_existing=False)

    eco.run(200, ecoalgorithm.ShowOutput.SHORT)

class TestIndividualPicker(TestCase):

    def test_test(self):
        initialize_sucess()

        # picker = IndividualPicker(get_some_cats())
        #
        # for i in range(30):
        #     fem = picker.pick_female()
        #     picker.pick_male(fem)
        #
        # print(picker.summary_str)


