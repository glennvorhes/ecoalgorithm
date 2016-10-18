import ecoalgorithm
from datetime import datetime

from ecoalgorithm._test.test_IndividualPicker import initialize_sucess

ecoalgorithm.config.multithread = False
# config.db_path = r'C:\xampp\htdocs\ecoalgorithm\r.db'


print('multithread', ecoalgorithm.config.multithread)

start = datetime.now()
initialize_sucess()

print(datetime.now() - start)
input('enter..')
