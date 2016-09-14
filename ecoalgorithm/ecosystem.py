from .species import Individual
from collections import defaultdict
import os
import json
import numpy as np
from datetime import datetime
from numpy.random import choice
from .species import Individual
from . import _helpers
from . import models
from . import db_connect
import sqlalchemy

__author__ = 'glenn'

db_conn = db_connect.db


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


def _breed_pair(the_female, the_male):
    """

    :param the_female:
    :param the_male:
    :type the_female: Individual
    :type the_male: Individual
    :return:
    """
    male_class = the_male.__class__

    assert the_female.__class__ == male_class

    if the_female.success is None or the_male.success is None:
        raise Exception('not mature')

    if the_female == the_male:
        raise Exception('no self breeding')

    out_list = []

    for i in range(male_class.get_offspring_count()):
        out_list.append(the_female.mate(the_male))

    return out_list


def _load_from_db():
    pass


def _clear_db():
    pass


def parse_generation(class_list):
    """

    :param class_list:
    :type: list[type]
    """
    class_dict = dict()
    """
    :type: dict[str, type]
    """

    db_inds = []

    for c in class_list:
        class_dict[c.__name__] = c

    lst_gen = db_conn.sess.query(models.DbGeneration).order_by(sqlalchemy.desc(
        models.DbGeneration.gen_num
    )).first()
    """
    :type: models.DbGeneration|None
    """

    if lst_gen:
        for individual in lst_gen.individuals:
            kw = json.loads(individual.kwargs)

            if individual.class_name not in class_dict:
                raise KeyError("Class name '{0}' not found in class list".format(
                    individual.class_name
                ))

            # TODO add check for required kwargs

            db_inds.append(
                class_dict[individual.class_name](
                    individual.success, **kw
                )
            )

    return db_inds


class OneGeneration(object):
    def __init__(self, this_generation=None, max_population=50, picker_power=2.0):
        """

        :param this_generation: immature individuals
        :param max_population: maximum population, stop breed operation when it has been reached
        :param picker_power: exponent for the decay of picker weighting TODO think about replacing with e derived weight
        :type this_generation: list[Individual]
        :type max_population: int
        :type picker_power: float
        :return:
        """

        self._this_generation = []

        if type(this_generation) is list:
            self._this_generation.extend(this_generation)

        self._dict_cls_name_species_list = defaultdict(list)
        """
        lookup list of individuals by class name
        :type: dict[str, list[Individual]]
        """

        self._species_set = set()
        """
        unique set of class names
        :type: set[str]
        """

        self._picker_power = picker_power
        """
        power to be used for the picker function
        :type: float
        """

        self._all_picker = _dummy_picker
        """
        dummy picker created before the real one is implemented
        :type: function
        """

        self._by_species_picker = {}
        """
        pickers but referenced by the individual species class names
        :type: dict[str, function]
        """

        self._max_population = max_population
        """
        maximum population, keep creating new individuals until the maximum population is reached
        :type: int
        """

        self._next_generation = []
        """
        list of individuals that will go on to the next generation
        :type: list[Individual]
        """

    def mature(self):
        """
        mature all the individuals and add to the species_dict lookup
        sort by all individuals
        set up the _population species pickers
        """

        # loop over all individuals
        for ind in self._this_generation:
            assert isinstance(ind, Individual)

            # only mature if not already, success is None when not mature
            if ind.success is None:
                ind.mature()

            # add individual to species list dict
            self._dict_cls_name_species_list[ind.__class__.__name__].append(ind)
            self._species_set.add(ind.__class__.__name__)

        # sort the individuals by success, highest first, set up the picker
        self._this_generation.sort(key=lambda x: x.success, reverse=True)
        self._all_picker = _helpers.individual_picker(self._this_generation, self._picker_power)

        # loop over the species
        for k, v in self._dict_cls_name_species_list.items():
            # sort the individuals in the by species list by success with highest first
            v.sort(key=lambda x: x.success, reverse=True)

            # create the weighted picker functions
            self._by_species_picker[k] = \
                _helpers.individual_picker(v, self._picker_power)

    def breed(self):
        """
        select the individuals to breed and reproduce
        """

        # start by breeding one pair from each species
        for picker in self._by_species_picker.values():
            female = picker()

            male = None

            while male is None or female == male:
                # pick from same species as female
                male = picker()
                """:type: Individual"""

            self._next_generation.extend(_breed_pair(female, male))

        while len(self._next_generation) < self._max_population:
            # pick first of pair from whole _population
            female = self._all_picker()
            """:type: Individual"""

            # initialize the male to None
            male = None

            # keep looping while the male is None or the male and female selection refer to the same
            while male is None or female == male:
                # pick from same species as female
                male = self._by_species_picker[female.__class__.__name__]()
                """:type: Individual"""

            # breed the two and append to the next generation
            self._next_generation.extend(_breed_pair(female, male))

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
        :rtype: list[Individual]
        """
        return self._next_generation

    @property
    def this_gen_individuals(self):
        """
        individuals in next generation

        :return: list of individuals
        :rtype: list[Individual]
        """
        return self._this_generation


class Ecosystem(object):
    """
    Management of species, individuals, and competition
    """

    def __init__(self,
                 new_individuals=None,
                 species_classes=None,
                 results_directory=None,
                 use_existing_results=True,
                 max_population=100,
                 picker_power=2.0,
                 offspring_count=None,
                 generation_limit=None
                 ):
        """
        initialize the population
        
        :param new_individuals: a list of new Individual objects to add to the population
        :param species_classes: a list of any classes not found in the new individuals list so ecosystem  knows how to 'repr'
        them from the existing results
        :param results_directory: the directory to contain the results, default 'results' folder in working directory
        :param use_existing_results: if should use existing results if available and continue
        :param max_population: the maximum population to create, can be overridden by sum (species * offspring)
        :param picker_power: decay power, higher values favor more successful individuals, default 2
        :param offspring_count: override the offspring count defined by the species classes
        :param generation_limit: limit on the number of generations run before exiting
        :type new_individuals: list|None
        :type results_directory: str|None
        :type use_existing_results: bool
        :type max_population: int
        :type picker_power: float
        :type offspring_count: int|None
        :type generation_limit: int|None
        """

        self._max_population = max_population
        self._picker_power = picker_power
        self._print_output = False
        self._generation_limit = generation_limit

        self._species_name_class_lookup = {}

        # the collection of all individuals
        self._population = []

        # append the new individuals if provided
        if new_individuals is not None:
            self._population.extend(new_individuals)

        # all _population weighed picker
        self._population_picker = _dummy_picker

        # access lists of individuals in _population, dict key is the species type (class)
        self._population_species_list_dict = defaultdict(list)

        # dictionary to choose an individual by species from the _population
        self._population_species_picker = {}

        # a set of unique species types/classes in the population, used to keep species persistence
        self._population_species_set = set()

        # generation initialized to 0, updated to last generation if loading existing results
        self._generation = 0

        new_individuals_class_set = set([ind.__class__ for ind in self._population])

        for cl in new_individuals_class_set:
            species_classes.append(cl)

        for cl in species_classes:
            if cl.__name__ not in self._species_name_class_lookup:
                self._species_name_class_lookup[cl.__name__] = cl

        # endregion

        # region set up the results directory and load existing if applicable
        if results_directory:
            self._results_directory = results_directory
        else:
            self._results_directory = os.path.join(os.getcwd(), 'results')

        # directory checking to make sure the expected directory and files exist
        self._use_existing_results = use_existing_results

        existing_result = self._get_existing_results()

        if isinstance(existing_result, list):
            self._population.extend(existing_result)

        # do some setup of the initial population

        # check to be sure there are at least two individuals
        if len(self._population) < 2:
            raise Exception('not enough individuals in population, need at least 2')

        # set of species in original _population, used to be sure at least
        # two individuals of a given species exists as generations progress
        species_count = defaultdict(int)

        species_class_set = set()
        min_population = 0

        for ind in self._population:
            if ind.__class__ not in species_class_set:
                species_class_set.add(ind.__class__)

                # override the class offspring count
                if offspring_count is not None:
                    ind.__class__.set_offspring_count(offspring_count)
                min_population += ind.__class__.get_offspring_count()
            species_count[ind.__class__.__name__] += 1

        for k in species_count:
            if species_count[k] < 2:
                raise Exception('species {0} has fewer than 2 individuals'.format(k))

        if self._max_population < min_population:
            self._max_population = min_population
            print('max population overridden: ' + str(self._max_population))

    def run(self, generation_limit=None, print_output=False, start_loop=True):
        """
        start running

        :param generation_limit: the number of generations to run, just keeps going if not defined
        :param print_output: print a summary of the population statistics
        :param start_loop: if the loop should start, for testing purposes
        :type generation_limit: int|None
        :type print_output: bool
        :type start_loop: bool
        """

        # region assign input parameters
        self._print_output = print_output

        generation_counter = 0

        if not start_loop:
            return

        # start the loop
        while True:

            generation_counter += 1

            if generation_limit is not None and generation_counter > generation_limit:
                break

            # increment generation
            self._generation += 1

            self._start_generation()

            # mature all individuals and set up the pickers, all _population and species specific
            self._mature_generation()

            # reproduce
            self._breed()

            # print the _population stats
            if print_output:
                self.show_population_stats()

            # write to file
            self._write_generation_to_file()

            self._population.clear()
            self._population.extend(self._next_generation)

    def _start_generation(self):
        """
        for the _population
        set picker to dummy picker and clear the species list dict and picker

        for the breeding _population
        clear the _population, set picker to dummy picker and clear the species list dict and picker

        clear the next generation
        """

        if self._print_output:
            print('!! generation: {0} !!'.format(self._generation))

        self._population_picker = _dummy_picker
        self._population_species_list_dict.clear()
        self._population_species_picker.clear()
        self._population_species_set.clear()

        self._next_generation.clear()

    def _get_existing_results(self):
        """
        check to make sure the results directory and all expected files exist

        :return: directory valid or not
        :rtype: list|None
        """
        can_use_existing = True
        return_val = None

        if not os.path.isdir(self._results_directory):
            os.mkdir(self._results_directory)
            can_use_existing = False

        if not os.path.isfile(self._results_file_all) or not self._use_existing_results:
            with open(self._results_file_all, 'w') as f:
                f.write('')
            can_use_existing = False

        if not os.path.isfile(self._results_file_best_individuals) or not self._use_existing_results:
            with open(self._results_file_best_individuals, 'w') as f:
                f.write('')
            can_use_existing = False

        if not os.path.isfile(self._results_file_latest_generation) or not self._use_existing_results:
            with open(self._results_file_latest_generation, 'w') as f:
                f.write('')
            can_use_existing = False
        else:
            with open(self._results_file_latest_generation, 'r') as f:
                try:
                    latest_gen_info = json.load(f)
                    self._generation = latest_gen_info['generation']

                    existing_individuals = []

                    for cls_param_dct in latest_gen_info['individuals']:
                        the_cls = self._species_name_class_lookup[cls_param_dct['class_name']]
                        the_params = cls_param_dct['params']
                        existing_individuals.append(the_cls(**the_params))

                    return_val = existing_individuals
                except ValueError:
                    return_val = None

        if can_use_existing and isinstance(return_val, list):
            return return_val
        else:
            return None

    def _mature_generation(self):
        pass

    def _breed(self):
        pass

    def _write_generation_to_file(self):
        """
        write out the current generation before passing the torch
        read the results file
        write with the latest mature individuals at the top
        """
        dte_string = datetime.now().strftime('%m/%d/%Y %H:%M:%S')

        with open(self._results_file_all, 'a') as f:
            f.write(json.dumps([repr(i) for i in self._population], indent=4) + '\n')

        with open(self._results_file_best_individuals, 'a') as f:
            f.write('{0}, gen {1}: {2}\n'.format(dte_string, self._generation, repr(self._population[0])))

        with open(self._results_file_latest_generation, 'w') as f:
            json.dump({
                'generation': self._generation,
                'date': dte_string,
                'individuals': [i.params() for i in self._population]
            }, f, indent=4)

        print('here')

        models.DbGeneration(self._population)
