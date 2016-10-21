import ecoalgorithm
import os
from ecoalgorithm import db, config
from ecoalgorithm._test.example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, \
    get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies
import multiprocessing

ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'results.db_445')
ecoalgorithm.config.multithread = False
from ecoalgorithm._helpers import printd


if __name__ == '__main__':
    db.clear_db()
    config.multithread = False

    eco = ecoalgorithm.Ecosystem(get_species_set(), get_some_inds(), use_existing=False, keep_all=False)
    eco.run(2, ecoalgorithm.ShowOutput.SHORT)
    eco.run(3, ecoalgorithm.ShowOutput.SHORT)
    eco.run(40, ecoalgorithm.ShowOutput.SHORT)

