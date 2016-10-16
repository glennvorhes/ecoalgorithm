from .db_connect import db
from ._config import config
from typing import Dict, List, Set
from ._models import Generation, SpeciesBase
from warnings import warn
from ._helpers import ShowOutput

__author__ = 'glenn'


class Ecosystem(object):
    """
    Management of species, individuals, and competition
    """

    def __init__(self,
                 species_set: Set[type],
                 new_individuals: List[SpeciesBase] = list(),
                 use_existing: bool = True,
                 max_population: int = 100,
                 keep_all: bool = True,
                 picker_power: float = 2.0,
                 multithread: bool = True
                 ):
        """
        initialize the population
        
        :param new_individuals: a list of new SpeciesBase objects to add to the population
        :param species_set: a set of any classes not found in the new individuals list so ecosystem
        them from the existing results
        :param use_existing: if should use existing results if available and continue
        :param max_population: the maximum population to create, can be overridden by sum (species * offspring)
        :param picker_power: decay power, higher values favor more successful individuals, default 2
        :type new_individuals: list[SpeciesBase]
        :type species_set: list[type]
        :type use_existing: bool
        :type max_population: int
        :type picker_power: float
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

        if type(picker_power) is int:
            picker_power = float(picker_power)

        assert type(picker_power) is float
        assert type(multithread) is bool

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

        if max_population < len(species_set) * 2:
            raise AssertionError('Max population must be two times the number of species')

        if use_existing:
            gen_num = Generation.get_current_generation_number()

            if gen_num is None:
                warn('no existing results, populate with new individuals')
                if len(new_individuals) == 2:
                    raise AssertionError('Not enough individuals to start')

                self._working_generation = Generation(
                    species_set, picker_power, multithread
                )
            else:
                self._working_generation = db.sess.query(Generation).filter(
                    Generation.gen_num == gen_num
                ).first()

                self._working_generation.__init__(species_set, picker_power, multithread)

        else:
            db.clear_db()
            if len(new_individuals) == 0:
                raise AssertionError('Not enough individuals to start')
            self._working_generation = Generation(species_set, picker_power, multithread)

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

        #
        #     # bail out if a generation limit has been set
        #     if generation_limit is not None and generation_counter > generation_limit:
        #         break
        #
        #     self._working_generation.mature()
        #     best_success = self._working_generation.best_success
        #
        #     # bail out if the percent change in best success is below a threshold for a defined number of generations
        #     # defaults to values set in config, initially 1% for 5 generations
        #     if last_gen_success is not None:
        #         chg_percent = abs((best_success - last_gen_success) / last_gen_success) * 100
        #
        #         if chg_percent < config.stop_threshold_percent:
        #             generations_below_threshold += 1
        #             if generations_below_threshold > config.stop_threshold_generations:
        #                 print("percent change less than {0}% for {1} generations".format(
        #                     config.stop_threshold_percent,
        #                     config.stop_threshold_generations
        #                 ))
        #                 break
        #         else:
        #             generations_below_threshold = 0
        #
        #     self._working_generation.breed()
        #
        #     self._working_generation.write_to_db()
        #
        #     if print_output == 'long':
        #         self._working_generation.print_stats()
        #     elif print_output == 'short':
        #         best_ind = self._working_generation.best_individual
        #         if best_ind is not None:
        #             print('Generation: {0}, Best success: {1}: {2}'.format(
        #                 self._generation_num,
        #                 best_ind.class_name,
        #                 best_ind.success
        #             ))
        #         else:
        #             print('Generation: {0}, No successful individuals'.format(
        #                 self._generation_num
        #             ))
        #
        #     self._working_generation = OneGeneration(
        #         self._working_generation.next_gen_individuals,
        #         self._max_population,
        #         self._picker_power
        #     )
        #
        #     last_gen_success = best_success
        #     generation_counter += 1
        #     self._generation_num += 1
        #
        # return generation_counter

    @property
    def working_generation(self) -> Generation:

        # for ind in self._working_generation.individuals:
        #     if ind.class_name == SpeciesBase.__name__:
        #         ind.__class__ = self.
        #         print('fix')
        #     # print(ind.class_name)
        # print(self._working_generation.individuals)

        return self._working_generation
