import ecoalgorithm
ecoalgorithm.config.db_path = '/home/glenn/PycharmProjects/ecoalgorithm/results.db'

from ecoalgorithm.web import app


app.run(port=5001, debug=True)
