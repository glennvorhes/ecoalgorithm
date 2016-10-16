import numpy as np
from numpy.random import choice
import ecoalgorithm
from typing import List
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
from enum import Enum


class ShowOutput(Enum):
    NONE = 0
    SHORT = 1
    LONG = 2


def breed(
        female: 'ecoalgorithm.SpeciesBase',
        male: 'ecoalgorithm.SpeciesBase') -> List['ecoalgorithm.SpeciesBase']:
    """
    Breed a pair of individuals

    :param female:
    :param male:
    :type female: ecoalgorithm.SpeciesBase
    :type male: ecoalgorithm.SpeciesBase
    :return:
    :rtype: list[ecoalgorithm.SpeciesBase]
    """
    assert type(female) is type(male)

    if not female.is_mature:
        raise AssertionError("individual 1 is not mature")

    if not male.is_mature:
        raise AssertionError("individual 2 is not mature")

    if not female.is_alive:
        raise AssertionError("individual 1 is not alive")

    if not male.is_alive:
        raise AssertionError("individual 2 is not alive")

    out_list = []
    """
    :type: list[ecoalgorithm.SpeciesBase]
    """
    offspring_count = female.get_offspring_count()

    while len(out_list) < offspring_count:
        new_ind = male.mate(female)
        new_ind._parent1_id = female.guid
        new_ind._parent2_id = male.guid
        out_list.append(new_ind)

    return out_list


def mature_individual(ind: 'ecoalgorithm.SpeciesBase'):
    if not ind.is_mature:
        ind.mature()


def mature_all(ind_list: List['ecoalgorithm.SpeciesBase'], multi_thread: bool = True):
    # TODO compare performance with single thread

    if multi_thread:
        pool = ThreadPool(cpu_count())
        pool.map(mature_individual, ind_list)
        pool.close()
        pool.join()
    else:
        for ind in ind_list:
            ind.mature()


class IndividualPicker:
    def __init__(self, ind_list: List['ecoalgorithm.SpeciesBase'], power: float = 2.0):
        """
        Make a chooser class

        :param ind_list: the items to be potentially picked
        :type ind_list: list[SpeciesBase]
        :param power: the power to which the picker decay function should be, use exp if not provided
        :type power: float|None
        """
        if type(power) is int:
            power = float(power)

        for j in ind_list:
            assert j.is_mature

        self._ind_list_all = ind_list

        self._ind_list = [i for i in ind_list if i.is_alive]

        self._ind_list.sort(key=lambda x: x.success, reverse=True)
        self._wgt = np.linspace(-1, 0, len(self._ind_list) + 1)

        self._wgt *= -1

        self._wgt **= power
        self._wgt = self._wgt[:-1]
        self._wgt /= np.sum(self._wgt)

    def pick_female(self) -> 'SpeciesBase':
        """
        Make weighted selection

        :return: the selection
        :rtype: SpeciesBase
        """
        return choice(self._ind_list, p=self._wgt)

    def pick_male(self, female) -> 'SpeciesBase':

        assert len(self._ind_list) > 1
        assert type(female) is type(self._ind_list[0])

        ix_female = self._ind_list.index(female)

        no_female = [self._ind_list[i] for i in range(len(self._ind_list)) if i != ix_female]
        no_female_weight = [self._wgt[i] for i in range(len(self._wgt)) if i != ix_female]
        no_female_weight /= np.sum(no_female_weight)

        return choice(no_female, p=no_female_weight)

    @property
    def num_alive(self):
        return len(self._ind_list)

    @property
    def has_two_alive(self) -> bool:
        return self.count_alive > 1

    @property
    def best_individual(self) -> 'SpeciesBase':
        if self.count_alive > 0:
            return self._ind_list[0]
        else:
            return None

    @property
    def count_alive(self) -> int:
        return len(self._ind_list)

    @property
    def count_dead(self) -> int:
        return self.count_all - self.count_alive

    @property
    def count_all(self) -> int:
        return len(self._ind_list_all)





# from . import _config
#
# import sqlalchemy
#
# from sqlalchemy.orm import relationship, Session
# from sqlalchemy import func
# from ecoalgorithm.species import SpeciesBase
# from sqlalchemy.orm import scoped_session, sessionmaker
# import atexit
# from ecoalgorithm import models
# from ecoalgorithm.models import IndividualPicker
#
#
# def individual_picker(ind_list, power=2):
#     """
#     Make a chooser function in a closure
#
#     :param ind_list: the items to be potentially picked
#     :type ind_list: list[SpeciesBase]
#     :param power: the power to which the picker decay function should be, use exp if not provided
#     :type power: float|None
#     :return: a chooser function
#     :rtype: function
#     """
#
#     ind_list = [i for i in ind_list if i.is_alive]
#
#     ind_list.sort(key=lambda x: x.success, reverse=True)
#
#     wgt = np.linspace(-1, 0, len(ind_list) + 1)
#     wgt *= -1
#
#     wgt **= power
#     wgt = wgt[:-1]
#     wgt /= np.sum(wgt)
#
#     def pick_female():
#         """
#         Make weighted selection
#
#         :return: the selection
#         :rtype: SpeciesBase
#         """
#         if len(ind_list) == 0:
#             return None
#         else:
#             return choice(ind_list, p=wgt)
#
#     return pick_female

#
# def picker_power_iterations(power, itr):
#     print('### power: {0}, iterations: {1} ###'.format(power, itr))
#     t = []
#     picker_count = OrderedDict()
#     for i in range(100):
#         t.append(i)
#         picker_count[str(i)] = 0
#
#     picker = IndividualPicker(t, power=power)
#
#     for i in range(itr):
#         pick_val = picker.pick_female()
#         picker_count[str(pick_val)] += 1
#
#     for k, v in picker_count.items():
#         print('{0}: {1}'.format(k, v))
#
#
# class TestHelper(TestCase):
#     def test_individual_picker(self):
#         picker_power_iterations(3, 1000)
#         picker_power_iterations(2, 1000)
#         # picker_power_iterations(1, 1000)
#         # picker_power_iterations(0, 1000)
#
