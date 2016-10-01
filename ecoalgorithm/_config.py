import os


class EcoConfig:

    def __init__(self):
        self._db_path = None
        self._stop_threshold_percent = 1.0
        self._stop_threshold_generations = 5
        # self._db_path = '/home/glenn/PycharmProjects/ecoalgorithm/ecoalgorithm/results.db'

    @property
    def db_path(self):
        """

        :return: path to sqlite db
        :rtype: str
        """
        if self._db_path is None:
            raise Exception('db path not defined, set ecoalgorithm.config.db_path first')
        return self._db_path

    @db_path.setter
    def db_path(self, db):
        """

        :param db:
        :type db: str
        """
        db = db.strip()
        try:
            assert os.path.isdir(os.path.dirname(db))
            assert db.endswith('.db')
        except AssertionError:
            raise AssertionError("The new db file has an invalid directory or does not end with .db")

        if self._db_path is not None and os.path.isfile(self._db_path):
            os.remove(self.db_path)

        self._db_path = db

    @property
    def stop_threshold_percent(self):
        """

        :return: threshold change after which to stop
        :rtype: float|None
        """
        return self._stop_threshold_percent

    @property
    def stop_threshold_generations(self):
        """

        :return: number of successive generations below threshold required to break
        :rtype: int|None
        """
        return self._stop_threshold_generations

config = EcoConfig()
