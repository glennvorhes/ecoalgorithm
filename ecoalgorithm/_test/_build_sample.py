import ecoalgorithm
import ecoalgorithm._test
from ecoalgorithm._test import test_ecosystem
import os

rerun = False

if __name__ == '__main__':
    if rerun:
        ecoalgorithm.db.delete_db()
        ecoalgorithm.config.db_path = os.path.join(
            os.getcwd(), 'results.db_test')
        ecoalgorithm.config.multithread = False

        test_ecosystem.build_example()
