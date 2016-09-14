from unittest import TestCase

from ecoalgorithm.ecosystem import Ecosystem
from test.example_species import Bird, Cat, Fish

from ecoalgorithm.models import DbGeneration

max_population = 40
offspring_count = 5


class TestEcosystem(TestCase):

    def setUp(self):
        self.inds = []

        Bird.set_offspring_count(7)

        Cat.set_offspring_count(4)

        for i in range(5):
            self.inds.append(Bird())
            self.inds.append(Cat())
            self.inds.append(Fish())

    def test_reinitialize_eco(self):
        self.ecosystem = Ecosystem(self.inds, species_classes=[Bird, Cat], use_existing_results=True,
                                   max_population=max_population, picker_power=2)


    # def test_set_run(self):
    #     self.test_reinitialize_eco()
    #     self.ecosystem.run(generation_limit=10, print_output=True, start_loop=True)
    #
    #
    # def test_start_generation(self):
    #     self.test_set_run()
    #     self.ecosystem._start_generation()
    #
    #     self.assertEquals(len(self.ecosystem._population_species_list_dict), 0)
    #     self.assertEquals(len(self.ecosystem._population_species_picker), 0)
    #     self.assertEquals(len(self.ecosystem._population_species_set), 0)
    #     self.assertEquals(len(self.ecosystem._next_generation), 0)
    #
    # def test_mature_generation(self):
    #     self.test_set_run()
    #     self.ecosystem._start_generation()
    #     self.ecosystem._mature_generation()
    #     self.ecosystem.show_population_stats()
    #
    # def test_breed(self):
    #     self.test_set_run()
    #     self.ecosystem._start_generation()
    #     self.ecosystem._mature_generation()
    #     self.ecosystem._breed()
    #     self.ecosystem.show_population_stats()
    #
    # def test_write_file(self):
    #     self.test_set_run()
    #     self.ecosystem._start_generation()
    #     self.ecosystem._mature_generation()
    #     self.ecosystem._breed()
    #     # self.ecosystem.show_population_stats()
    #     self.ecosystem._write_generation_to_file()
    #
    # def test_write_generation(self):
    #     DbGeneration([])

