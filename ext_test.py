import ecoalgorithm
from datetime import datetime

from ecoalgorithm._test.test_IndividualPicker import initialize_sucess

from ecoalgorithm import config
config.multithread = False

print('multithread', config.multithread)

start = datetime.now()
initialize_sucess()

print(datetime.now() - start)
input('enter..')
