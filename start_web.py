import ecoalgorithm
from ecoalgorithm import start_web_server
import os

ecoalgorithm.config.db_path = os.path.join(
    os.getcwd(), 'ecoalgorithm', '_test', 'results.db_test')

start_web_server(5002, True)
