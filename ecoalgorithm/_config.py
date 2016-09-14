import os


class EcoConfig:

    def __init__(self):
        # self._db_path = os.path.join(os.getcwd(), 'results.db')
        self._db_path = '/home/glenn/PycharmProjects/ecoalgorithm/ecoalgorithm/results2.db'

    @property
    def db_path(self):
        """

        :return: path to sqlite db
        :rtype: str
        """
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

        if os.path.isfile(self._db_path):
            os.remove(self.db_path)

        self._db_path = db

config = EcoConfig()
