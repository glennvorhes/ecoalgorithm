from ._db_connect import db
from ._config import config
from typing import Dict, List, Set
from ._models import Generation, SpeciesBase
from warnings import warn
from ._helpers import ShowOutput
from . import config
from datetime import datetime

__author__ = 'glenn'


class Ecosystem(object):
    """
    Management of species, individuals, and competition
    """

    def __init__(self,
                 species_set: Set[SpeciesBase.__class__],
                 new_individuals: List[SpeciesBase] = list(),
                 use_existing: bool = True,
                 max_population: int = 100,
                 keep_all: bool = True
                 ):
        """
        initialize the population
        
        :param new_individuals: a list of new SpeciesBase objects to add to the population
        :param species_set: a set of any classes not found in the new individuals list so ecosystem
        them from the existing results
        :param use_existing: if should use existing results if available and continue
        :param max_population: the maximum population to create, can be overridden by sum (species * offspring)
        :type new_individuals: list[SpeciesBase]
        :type species_set: list[type]
        :type use_existing: bool
        :type max_population: int
        """

        # validate inputs
        assert type(species_set) is set
        assert len(species_set) > 0

        for s in species_set:
            assert issubclass(s, SpeciesBase)
            assert s.__name__ != SpeciesBase.__name__

        assert type(new_individuals) is list

        for ind in new_individuals:
            assert issubclass(type(ind), SpeciesBase)
            assert ind.__class__.__name__ != SpeciesBase.__name__

        assert type(use_existing) is bool

        assert type(max_population) is int

        assert type(keep_all) is bool

        self._max_population = max_population
        self._keep_all = keep_all

        self._working_generation = None
        """
        :type: Generation
        """

        for ind in new_individuals:
            species_set.add(ind.__class__)

        # validate the species classes
        for s in species_set:

            s.validate_class()

        required_max = 0
        for s in species_set:
            required_max += s.get_offspring_count()

        if max_population < required_max:
            raise AssertionError('Max population must be greater than the sum of class offspring counts')

        if use_existing:
            gen_num = Generation.get_current_generation_number()

            if gen_num is None:
                warn('no existing results, populate with new individuals')
                if len(new_individuals) == 2:
                    raise AssertionError('Not enough individuals to start')

                self._working_generation = Generation(species_set)
            else:
                self._working_generation = db.sess.query(Generation).filter(
                    Generation.gen_num == gen_num
                ).first()

                self._working_generation.__init__(species_set)

        else:
            db.clear_db()
            if len(new_individuals) == 0:
                raise AssertionError('Not enough individuals to start')
            self._working_generation = Generation(species_set)

        if new_individuals:
            self._working_generation.add_individuals(new_individuals)

        self._working_generation.save()

    def run(self, generation_limit=None, show_output: ShowOutput=ShowOutput.NONE, break_threshold: float=1):
        """
        start running

        :param generation_limit: the number of generations to run, just keeps going if not defined
        :param show_output: print a summary of the population statistics options
        :param break_threshold: threshold as whole number percent, break if the change between successive generations
        is less than this value
        :type generation_limit: int|None
        :type show_output: ShowOutput
        """
        assert isinstance(self._working_generation, Generation)

        assert type(show_output) is ShowOutput

        if generation_limit is not None:
            assert type(generation_limit) is int

        if break_threshold is not None:
            if type(break_threshold) is int:
                break_threshold = float(break_threshold)
            assert type(break_threshold) is float
            if not 0 < break_threshold <= 5:
                raise AssertionError('break threshold must be greater than 0 and less than or equal to 5')
            break_threshold /= 100

        generation_counter = 0

        no_success_generation_count = 0

        last_gen_success = self._working_generation.best_success
        generations_below_threshold_count = 0

        # start the loop
        while True:

            start_time = datetime.now()

            if type(generation_limit) is int:
                generation_counter += 1

                if generation_counter > generation_limit:
                    break

            if not self._working_generation.populate_next_generation(self._max_population, self._keep_all):
                warn("No living individuals and keep all flag set to false, exiting loop")
                break

            if show_output == ShowOutput.SHORT:
                print(self._working_generation.summary_short)
            elif show_output == ShowOutput.LONG:
                print(self._working_generation.summary_long)

            this_gen_sucess = self._working_generation.best_success

            if this_gen_sucess is None:
                generations_below_threshold_count = 0
                no_success_generation_count += 1
                if no_success_generation_count > 10:
                    warn("10 generations with no successful individuals, breaking loop")
                    break
            else:
                no_success_generation_count = 0

                if break_threshold is not None and last_gen_success is not None:
                    change_percent = abs((last_gen_success - this_gen_sucess) / last_gen_success)

                    if change_percent < break_threshold:
                        generations_below_threshold_count += 1

                        if generations_below_threshold_count > 5:
                            msg = "5 generations with change less than {0}%".format(
                                break_threshold * 100
                            )
                            warn(msg)
                            break
                    else:
                        generations_below_threshold_count = 0

                    last_gen_success = this_gen_sucess

            self._working_generation = self._working_generation.next_generation

            if show_output in (ShowOutput.SHORT, ShowOutput.LONG):
                print('\tProcessing Time: {0}'.format(datetime.now() - start_time))

    @property
    def working_generation(self) -> Generation:

        # for ind in self._working_generation.individuals:
        #     if ind.class_name == SpeciesBase.__name__:
        #         ind.__class__ = self.
        #         print('fix')
        #     # print(ind.class_name)
        # print(self._working_generation.individuals)

        return self._working_generation
