import ecoalgorithm
import os
from ecoalgorithm import db, config
from ecoalgorithm._test.example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, \
    get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies
import multiprocessing

ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'results.db_446')
ecoalgorithm.config.multithread = False

ecoalgorithm.start_web_server(5002, True)

