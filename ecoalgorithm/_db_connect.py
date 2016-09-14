from ._config import db_path
import sqlalchemy as _sqlalchemy
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import scoped_session as _scoped_session, \
    sessionmaker as _sessionmaker
import atexit as _atexit


__all__ = ['db']


class _DbConnect:
    def __init__(self):
        self._engine = _sqlalchemy.create_engine('sqlite:///' + db_path)

        self._session_maker = None

    @property
    def engine(self):
        return self._engine

    @property
    def sess(self):
        """
        return the existing session if it exists
        :return:
        :rtype: _Session
        """

        if self._session_maker is None:
            self._session_maker = _scoped_session(_sessionmaker(bind=self.engine))

        return self._session_maker()

    def close_connection(self):
        if self._session_maker is not None:
            self._session_maker.remove()




db = _DbConnect()

_atexit.register(db.close_connection)
