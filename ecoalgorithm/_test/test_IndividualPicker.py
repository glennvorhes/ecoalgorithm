from .example_species import get_some_inds, Cat
from unittest import TestCase
import ecoalgorithm
from .._helpers import IndividualPicker, mature_all


def get_some_cats():
    out_inds = []

    for i in range(50):
        out_inds.append(Cat())

    mature_all(out_inds)

    return out_inds


class TestIndividualPicker(TestCase):


    def test_test(self):

        picker = IndividualPicker(get_some_cats(), 2.0)

        for i in range(30):
            fem = picker.pick_female()
            picker.pick_male(fem)

        print(picker.summary_str)


