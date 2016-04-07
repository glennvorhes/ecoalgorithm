from .species import Individual
from collections import defaultdict
import os
import json
import numpy as np
from numpy.random import choice
from datetime import datetime

__author__ = 'glenn'


def _individual_picker(ind_list, power=2):
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
                 offspring_count=None
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
        :type new_individuals: list|None
        :type results_directory: str|None
        :type use_existing_results: bool
        :type max_population: int
        :type picker_power: float
        :type offspring_count: int|None
        """

        self._max_population = max_population
        self._picker_power = picker_power
        self._print_output = False

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

        # individuals in the next generation
        self._next_generation = []

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

        self._results_file_all = os.path.join(self._results_directory, 'results_all.txt')
        self._results_file_best_individuals = os.path.join(self._results_directory, 'best_individuals.txt')
        self._results_file_latest_generation = os.path.join(self._results_directory, 'latest_generation.json')

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
        """
        mature all the individuals and add to the species_dict lookup
        sort by all individuals
        set up the _population species pickers
        """

        # loop over all individuals
        for ind in self._population:
            assert isinstance(ind, Individual)

            # only mature if not already, success is None when not mature
            if ind.success is None:
                ind.mature()

            # add individual to species list dict
            self._population_species_list_dict[ind.__class__.__name__].append(ind)
            self._population_species_set.add(ind.__class__.__name__)

        # sort the individuals by success, highest first, set up the picker
        self._population.sort(key=lambda x: x.success, reverse=True)
        self._population_picker = _individual_picker(self._population, self._picker_power)

        # loop over the species
        for k in self._population_species_list_dict:
            # sort the individuals in the by species list by success with highest first
            self._population_species_list_dict[k].sort(key=lambda x: x.success, reverse=True)

            # create the weighted picker functions
            self._population_species_picker[k] = \
                _individual_picker(self._population_species_list_dict[k], self._picker_power)

    def _breed(self):
        """
        select the individuals to breed and reproduce
        """

        # start by breeding one pair from each species
        for picker in self._population_species_picker.values():
            female = picker()

            male = None

            while male is None or female == male:
                # pick from same species as female
                male = picker()
                """:type: Individual"""

            self._next_generation.extend(_breed_pair(female, male))

        while len(self._next_generation) < self._max_population:
            # pick first of pair from whole _population
            female = self._population_picker()
            """:type: Individual"""

            # initialize the male to None
            male = None

            # keep looping while the male is None or the male and female selection refer to the same
            while male is None or female == male:
                # pick from same species as female
                male = self._population_species_picker[female.__class__.__name__]()
                """:type: Individual"""

            # breed the two and append to the next generation
            progeny_list = _breed_pair(female, male)

            available_spots = self._max_population - len(self._next_generation)

            if len(progeny_list) > available_spots:
                self._next_generation.extend(progeny_list[:available_spots])
            else:
                self._next_generation.extend(progeny_list)

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
                'individuals': [i.to_dict() for i in self._population]
            }, f, indent=4)

    def show_population_stats(self):
        """
        print out the population statistics
        """

        out_string = '## population statistics ##\n'
        out_string += self._print_population_stats_helper('all')
        out_string += self._print_population_stats_helper('next_gen')
        out_string += '## end stats ##'
        print(out_string)

    def _print_population_stats_helper(self, selected_population):
        """
        helper to create the _population statistics output
        :param selected_population: one of following: 'all', 'breeding', 'next_gen'
        :type selected_population: string
        :return: stats specific to this _population
        :rtype: string
        """

        assert selected_population in ['all', 'breeding', 'next_gen']

        if selected_population == 'all':
            population_label = 'Population'
            full_list = self._population
            species_list_dict = self._population_species_list_dict
        elif selected_population == 'next_gen':
            population_label = 'Next Generation'
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
                unique_species = [k for k in self._population_species_list_dict.keys()]
                unique_species.sort()
                for k in unique_species:
                    species_stats = _calc_population_stats(species_list_dict[k])
                    out_string += species_template.format(k, *species_stats)

        return out_string
