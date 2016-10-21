import os
import re

class EcoConfig:

    def __init__(self):
        self._db_path = None
        self._stop_threshold_percent = 1.0
        self._stop_threshold_generations = 5
        self._web_port = 5001
        self._web_debug = True
        self._db_path = os.path.join(os.getcwd(), 'results.db')
        self._multithread = True
        self._picker_weight = 4.0

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
            assert re.search(r'\.(db_test|db_\d{3})$', '.db_123')
        except AssertionError:
            raise AssertionError("The new db file has an invalid directory or does not end with .db")

        # if self._db_path is not None and os.path.isfile(self._db_path):
        #     os.remove(self.db_path)

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

    @property
    def web_port(self):
        """

        :return:
        :rtype: int
        """
        return self._web_port

    @web_port.setter
    def web_port(self, port):
        self._web_port = port

    @property
    def web_debug(self):
        """

        :return: web debug
        :rtype: bool
        """
        return self._web_debug

    @web_debug.setter
    def web_debug(self, debug):
        """

        :param debug:
        :type debug: bool
        """
        self._web_debug = debug

    @property
    def multithread(self):
        return self._multithread

    @multithread.setter
    def multithread(self, multi):
        assert isinstance(multi, bool)
        self._multithread = multi

    @property
    def picker_weight(self):
        return self._picker_weight

    @picker_weight.setter
    def picker_weight(self, weight):
        if isinstance(weight, int):
            weight = float(weight)
        assert isinstance(weight, float)
        assert 0 <= weight <= 100
        self._picker_weight = weight

config = EcoConfig()
