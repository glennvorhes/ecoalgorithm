from .species import SpeciesBase
from collections import defaultdict
import os
import json
import numpy as np
from datetime import datetime
from numpy.random import choice
from .species import SpeciesBase
from . import _helpers
from . import models
import sqlalchemy
from .db_connect import db
from ._config import config
from ._helpers import IndividualPicker
from enum import Enum
from typing import Dict, List, Set

__author__ = 'glenn'


def _dummy_picker():
    raise Exception('Should never really call the dummy picker')


def _calc_population_stats(pop_list):
    """
    given the _population, return a tuple with count, mature count, and immature count

    :param pop_list: the _population list
    :type pop_list: list
    :return: return a tuple with count, mature count, and immature count
    :rtype: tuple
    """
    count = 0
    mature_count = 0
    immature_count = 0

    for ind in pop_list:
        count += 1
        if ind.success is None:
            immature_count += 1
        else:
            mature_count += 1

    return count, mature_count, immature_count


def _load_from_db():
    pass


def _clear_db():
    pass


def parse_generation(class_list):
    """

    :param class_list:
    :type: list[type]
    :returns: list of individuals in the most recent generation
    :rtype: (list[SpeciesBase], int)
    """
    class_dict = dict()
    """
    :type: dict[str, type]
    """

    db_inds = []
    the_generation = 1

    for c in class_list:
        class_dict[c.__name__] = c

    lst_gen = db.sess.query(models.DbGeneration).order_by(sqlalchemy.desc(
        models.DbGeneration.gen_num
    )).first()
    """
    :type: models.DbGeneration|None
    """

    if lst_gen:
        the_generation = lst_gen.gen_num
        for individual in lst_gen.individuals:
            kw = json.loads(individual.kwargs)

            if individual.class_name not in class_dict:
                raise KeyError("Class name '{0}' not found in class list".format(
                    individual.class_name
                ))

            new_ind = class_dict[individual.class_name](
                individual.success, **kw
            )
            """
            :type: SpeciesBase
            """

            new_ind.parent1 = individual.parent1
            new_ind.parent2 = individual.parent2
            new_ind.guid = individual.guid

            db_inds.append(new_ind)

    return db_inds, the_generation


class OneGeneration(object):
    def __init__(self, start_population, max_population=50, picker_power=2.0):
        """

        :param start_population: immature individuals
        :param max_population: maximum population, stop breed operation when it has been reached
        :param picker_power: exponent for the decay of picker weighting TODO think about replacing with e derived weight
        :type start_population: list[SpeciesBase]
        :type max_population: int
        :type picker_power: float
        :return:
        """

        self._matured = False

        self._this_generation = start_population
        """
        input population
        :type: list[SpeciesBase]
        """

        self._dict_cls_name_species_list = defaultdict(list)
        """
        lookup list of individuals by class name
        :type: dict[type, list[SpeciesBase]]
        """

        self._species_set = set()
        """
        unique set of class names
        :type: set[type]
        """

        self._picker_power = picker_power
        """
        power to be used for the picker function
        :type: float
        """

        self._all_picker = IndividualPicker([], 2)
        """
        dummy picker created before the real one is implemented
        :type: IndividualPicker
        """

        self._by_species_picker = {}
        """
        pickers but referenced by the individual species class names
        :type: dict[type, IndividualPicker]
        """

        self._max_population = max_population
        """
        maximum population, keep creating new individuals until the maximum population is reached
        :type: int
        """

        self._next_generation = []
        """
        list of individuals that will go on to the next generation
        :type: list[SpeciesBase]
        """

        # loop over all individuals
        for ind in self._this_generation:

            # only mature if not already, success is None when not mature
            if ind.success is None:
                ind.mature()

            # add individual to species list dict
            self._dict_cls_name_species_list[ind.__class__].append(ind)
            self._species_set.add(ind.__class__)

        # validation
        for k, v in self._dict_cls_name_species_list.items():
            try:
                assert len(v) >= 2
            except AssertionError:
                raise AssertionError('each species must have two or more individuals')

    def mature(self):
        """
        mature all the individuals and add to the species_dict lookup
        sort by all individuals
        set up the _population species pickers
        """

        if self._matured:
            return

        # loop over all individuals
        for ind in self._this_generation:

            # only mature if not already, success is None when not mature
            if ind.success is None:
                ind.mature()

        # sort the individuals by success, highest first, set up the picker
        self._all_picker = IndividualPicker(self._this_generation, self._picker_power)

        # loop over the species
        for k, v in self._dict_cls_name_species_list.items():
            # create the weighted picker functions
            self._by_species_picker[k] = IndividualPicker(v, self._picker_power)

        self._matured = True

    def breed(self):
        """
        select the individuals to breed and reproduce
        """

        some_alive = self._all_picker.num_alive > 1
        # if not some_alive:
        #     raise Exception('they are all dead')

        # start by breeding one pair from each species
        for the_cls, picker in self._by_species_picker.items():
            if picker.num_alive > 1:
                female = picker.pick_female()
                male = picker.pick_male(female)
                self._next_generation.extend(_breed_pair(female, male))
            else:
                for i in range(the_cls().get_offspring_count()):
                    self._next_generation.append(the_cls())

        while len(self._next_generation) < self._max_population:
            if some_alive:
                # pick_female first of pair from whole _population
                female = self._all_picker.pick_female()
                pic = self._by_species_picker[female.__class__]

                if pic.num_alive < 2:
                    continue

                male = pic.pick_male(female)

                # breed the two and append to the next generation
                self._next_generation.extend(_breed_pair(female, male))

            else:
                for s in self._species_set:
                    for i in range(s().get_offspring_count()):
                        self._next_generation.append(s())

        if len(self._next_generation) > self._max_population:
            self._next_generation = self._next_generation[:self._max_population]

    def write_to_db(self):
        models.DbGeneration(self.this_gen_individuals)

    def print_stats(self):
        """
        print out the population statistics
        """

        out_string = '## population statistics ##\n'
        out_string += self._print_population_stats_helper('all')
        out_string += self._print_population_stats_helper('next_gen_individuals')
        out_string += '## end stats ##'
        print(out_string)

    def _print_population_stats_helper(self, selected_population):
        """
        helper to create the _population statistics output
        :param selected_population: one of following: 'all', 'breeding', 'next_gen_individuals'
        :type selected_population: string
        :return: stats specific to this _population
        :rtype: string
        """

        assert selected_population in ['all', 'breeding', 'next_gen_individuals']

        if selected_population == 'all':
            population_label = 'Population'
            full_list = self._this_generation
            species_list_dict = self._dict_cls_name_species_list
        elif selected_population == 'next_gen_individuals':
            population_label = 'Next DbGeneration'
            full_list = self._next_generation
            species_list_dict = defaultdict(list)
            for ind in self._next_generation:
                species_list_dict[ind.__class__.__name__].append(ind)
        else:
            raise Exception('_population identifier invalid')

        all_template = '\t\tcount: {0}, mature: {1}, immature: {2}\n'
        species_template = '\t\t{0}, count: {1}, mature: {2}, immature: {3}\n'

        if len(full_list) == 0:
            out_string = '\t{0} is empty\n'.format(population_label)
        else:
            out_string = '\t{0}\n'.format(population_label)
            if selected_population == 'breeding' and full_list[0].success is not None:
                out_string += '\t\tBest: {0}\n'.format(repr(full_list[0]))
            pop_stats = _calc_population_stats(full_list)
            out_string += all_template.format(*pop_stats)

            if len(species_list_dict) == 0:
                out_string += '{0} species list dict not set up'.format(population_label)
            else:
                unique_species = [k for k in self._dict_cls_name_species_list.keys()]
                unique_species.sort()
                for k in unique_species:
                    species_stats = _calc_population_stats(species_list_dict[k])
                    out_string += species_template.format(k, *species_stats)

        return out_string

    @property
    def next_gen_individuals(self):
        """
        individuals in next generation

        :return: list of individuals
        :rtype: list[SpeciesBase]
        """
        return self._next_generation

    @property
    def this_gen_individuals(self):
        """
        individuals in next generation

        :return: list of individuals
        :rtype: list[SpeciesBase]
        """
        return self._this_generation

    @property
    def best_success(self):
        best_ind = self.best_individual

        if best_ind is None:
            return None
        else:
            return best_ind.success

    @property
    def best_individual(self):
        """


        :return:
        :rtype: SpeciesBase|None
        """
        if not self._matured:
            self.mature()

        alive_inds = [i for i in self.this_gen_individuals if i.is_alive]

        if len(alive_inds) == 0:
            return None
        else:
            alive_inds.sort(key=lambda x: x.success, reverse=True)
            return alive_inds[0]


class Ecosystem(object):
    """
    Management of species, individuals, and competition
    """

    def __init__(self,
                 species_set: Set[type],
                 new_individuals: List[models.SpeciesBase] = list(),
                 use_existing_results: bool = True,
                 max_population: int = 100,
                 keep_all:bool = True,
                 picker_power: float = 2.0
                 ):
        """
        initialize the population
        
        :param new_individuals: a list of new SpeciesBase objects to add to the population
        :param species_set: a set of any classes not found in the new individuals list so ecosystem
        them from the existing results
        :param use_existing_results: if should use existing results if available and continue
        :param max_population: the maximum population to create, can be overridden by sum (species * offspring)
        :param picker_power: decay power, higher values favor more successful individuals, default 2
        :type new_individuals: list[SpeciesBase]
        :type species_set: list[type]
        :type use_existing_results: bool
        :type max_population: int
        :type picker_power: float
        """

        self._max_population = max_population
        self._picker_power = picker_power
        self._print_output = False
        self._keep_all = keep_all
        self._species_set = species_set
        self._working_generation = None
        """
        :type: models.Generation
        """

        if use_existing_results:
            gen_num = models.Generation.get_current_generation_number()

            if gen_num is None:
                print('no existing results')
                if len(new_individuals) < 2:
                    print('not enough individuals to start')
                    raise Exception('Not enough individuals to start')

                self._working_generation = models.Generation()

            else:
                self._working_generation = db.sess.query(models.Generation).filter(
                    models.Generation.gen_num == gen_num
                ).first()
                self._working_generation.fix_species_classes(self._species_set)

        else:
            db.clear_db()
            if len(new_individuals) < 2:
                print('not enough individuals to start')
                raise Exception('Not enough individuals to start')
            self._working_generation = models.Generation()

        self._species_set = self._working_generation.add_individuals(new_individuals)
        self._working_generation.save()

    def run(self, generation_limit=None, print_output=None):
        """
        start running

        :param generation_limit: the number of generations to run, just keeps going if not defined
        :param print_output: print a summary of the population statistics options are 'short' and 'long'
        :type generation_limit: int|None
        :type print_output: str|None
        """

        generation_counter = 0
        last_gen_success = None
        generations_below_threshold = 1

        # start the loop
        while True:

            # bail out if a generation limit has been set
            if generation_limit is not None and generation_counter > generation_limit:
                break

            self._working_generation.mature()
            best_success = self._working_generation.best_success

            # bail out if the percent change in best success is below a threshold for a defined number of generations
            # defaults to values set in config, initially 1% for 5 generations
            if last_gen_success is not None:
                chg_percent = abs((best_success - last_gen_success) / last_gen_success) * 100

                if chg_percent < config.stop_threshold_percent:
                    generations_below_threshold += 1
                    if generations_below_threshold > config.stop_threshold_generations:
                        print("percent change less than {0}% for {1} generations".format(
                            config.stop_threshold_percent,
                            config.stop_threshold_generations
                        ))
                        break
                else:
                    generations_below_threshold = 0

            self._working_generation.breed()

            self._working_generation.write_to_db()

            if print_output == 'long':
                self._working_generation.print_stats()
            elif print_output == 'short':
                best_ind = self._working_generation.best_individual
                if best_ind is not None:
                    print('Generation: {0}, Best success: {1}: {2}'.format(
                        self._generation_num,
                        best_ind.class_name,
                        best_ind.success
                    ))
                else:
                    print('Generation: {0}, No successful individuals'.format(
                        self._generation_num
                    ))

            self._working_generation = OneGeneration(
                self._working_generation.next_gen_individuals,
                self._max_population,
                self._picker_power
            )

            last_gen_success = best_success
            generation_counter += 1
            self._generation_num += 1

        return generation_counter
