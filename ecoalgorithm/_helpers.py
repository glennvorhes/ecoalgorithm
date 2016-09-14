from unittest import TestCase
import numpy as np
from numpy.random import choice
from collections import OrderedDict
from . import _config

import sqlalchemy

from sqlalchemy.orm import relationship, Session
from sqlalchemy import func
from ecoalgorithm.species import Individual
from sqlalchemy.orm import scoped_session, sessionmaker
import atexit
from ecoalgorithm import models


def individual_picker(ind_list, power=2):
    """
    Make a chooser function in a closure

    :param ind_list: the items to be potentially picked
    :type ind_list: list
    :param power: the power to which the picker decay function should be, use exp if not provided
    :type power: float|None
    :return: a chooser function
    :rtype: function
    """
    wgt = np.linspace(-1, 0, len(ind_list) + 1)
    wgt *= -1

    wgt **= power
    wgt = wgt[:-1]
    wgt /= np.sum(wgt)

    def pick():
        """
        Make weighted selection

        :return: the selection
        :rtype: Individual
        """
        return choice(ind_list, p=wgt)

    return pick


def picker_power_iterations(power, itr):
    print('### power: {0}, iterations: {1} ###'.format(power, itr))
    t = []
    picker_count = OrderedDict()
    for i in range(100):
        t.append(i)
        picker_count[str(i)] = 0

    picker = individual_picker(t, power=power)

    for i in range(itr):
        pick_val = picker()
        picker_count[str(pick_val)] += 1

    for k, v in picker_count.items():
        print('{0}: {1}'.format(k, v))


class TestHelper(TestCase):
    def test_individual_picker(self):
        picker_power_iterations(3, 1000)
        picker_power_iterations(2, 1000)
        # picker_power_iterations(1, 1000)
        # picker_power_iterations(0, 1000)

