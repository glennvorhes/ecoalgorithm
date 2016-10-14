import sqlalchemy as _sqlalchemy
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import scoped_session as _scoped_session, \
    sessionmaker as _sessionmaker
import atexit as _atexit
import os
from sqlalchemy import exc
from ._config import config


__all__ = ['db']


class _DbConnect:
    def __init__(self):

        self._db_path = None
        self._db_string = None
        self._checked = False
        self._session_maker = None
        self._engine = None
        self._session_maker = None
        self._sub_init()

    def _sub_init(self):
        self._db_path = config.db_path
        self._db_string = 'sqlite:///' + self._db_path
        self._checked = False
        self._session_maker = None
        self._engine = _sqlalchemy.create_engine(self._db_string)
        self._session_maker = None

    @property
    def engine(self):
        if self._db_path != config.db_path:
            self._sub_init()

        return self._engine

    @property
    def sess(self):
        """
        return the existing session if it exists
        :return:
        :rtype: _Session
        """
        if self._db_path != config.db_path:
            self._sub_init()

        if self._session_maker is None:
            self._session_maker = _scoped_session(_sessionmaker(bind=self.engine))

        sess = self._session_maker()
        """
        :type: _Session

        """

        if not self._checked:
            from . import models
            try:
                sess.query(models.Generation).first()
            except exc.OperationalError:
                models.create_db()
        self._checked = True

        return self._session_maker()

    def close_connection(self):
        if self._session_maker is not None:
            self._session_maker.remove()
            self._session_maker = None
        self._checked = False

    def clear_db(self):
        from . import models
        self.sess.query(models.SpeciesBase).delete()
        self.sess.commit()
        self.sess.query(models.Generation).delete()
        self.sess.commit()

    def delete_db(self):
        self.close_connection()
        try:
            os.remove(self._db_path)
        except FileNotFoundError:
            pass

        self._checked = False

db = _DbConnect()

_atexit.register(db.close_connection)
