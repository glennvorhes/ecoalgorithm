from .db_connect import db
from ._config import config
from typing import Dict, List, Set
from ._models import Generation, SpeciesBase


__author__ = 'glenn'


class Ecosystem(object):
    """
    Management of species, individuals, and competition
    """

    def __init__(self,
                 species_set: Set[type],
                 new_individuals: List[SpeciesBase] = list(),
                 use_existing_results: bool = True,
                 max_population: int = 100,
                 keep_all: bool = True,
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

        assert len(species_set) > 0
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
            gen_num = Generation.get_current_generation_number()

            if gen_num is None:
                print('no existing results')
                if len(new_individuals) < 2:
                    print('not enough individuals to start')
                    raise Exception('Not enough individuals to start')

                self._working_generation = Generation(
                    self._species_set
                )
            else:
                self._working_generation = db.sess.query(Generation).filter(
                    Generation.gen_num == gen_num
                ).first()
                self._working_generation.fix_species_classes(self._species_set)

        else:
            db.clear_db()
            if len(new_individuals) == 0:
                raise Exception('Not enough individuals to start')
            self._working_generation = Generation(self._species_set)

        if new_individuals:
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

    @property
    def working_generation(self) -> Generation:

        # for ind in self._working_generation.individuals:
        #     if ind.class_name == SpeciesBase.__name__:
        #         ind.__class__ = self.
        #         print('fix')
        #     # print(ind.class_name)
        # print(self._working_generation.individuals)

        return self._working_generation
