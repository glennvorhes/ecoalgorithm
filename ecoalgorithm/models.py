import sqlalchemy
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ecoalgorithm._config import db_path
from ecoalgorithm import _helpers
from ecoalgorithm._db_connect import db
from ecoalgorithm.species import Individual
import json


__all__ = ['create_db']

Base = declarative_base(bind=db.engine)


class DbGeneration(Base):
    __tablename__ = 'generation'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, index=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, index=True, unique=True, nullable=False)
    gen_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    individuals = relationship('_DbIndividual', backref='generation')
    """
    :type: list[_DbIndividual]
    """

    def __init__(self, individual_list=None):
        """

        :param individual_list:
        :type individual_list: list[Individual]
        :return:
        """
        last_gen = db.sess.query(DbGeneration.gen_num).order_by(sqlalchemy.desc(DbGeneration.gen_num)).first()

        if last_gen is None or last_gen[0] is None:
            self.gen_num = 1
        else:
            self.gen_num = last_gen[0] + 1
        db.sess.add(self)
        db.sess.commit()

        for ind in individual_list:
            db.sess.add(_DbIndividual(self.gen_num, ind))

        db.sess.commit()

    __table_args__ = {'sqlite_autoincrement': True}


class _DbIndividual(Base):
    __tablename__ = 'individual'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, sqlalchemy.ForeignKey(DbGeneration.gen_num))
    class_name = sqlalchemy.Column(sqlalchemy.String)
    success = sqlalchemy.Column(sqlalchemy.Float)
    kwargs = sqlalchemy.Column(sqlalchemy.String)

    __table_args__ = (
        sqlalchemy.Index('ix_gen_success', 'gen_num', 'success'),
        {'sqlite_autoincrement': True},
    )

    def __init__(self, gen_num, ind):
        """

        :param gen_num:
        :param ind:
        :type gen_num: int
        :type ind: Individual
        """
        self.gen_num = gen_num
        self.class_name = ind.class_name

        self.kwargs = json.dumps(ind.params())
        self.success = ind.success


def create_db():

    Base.metadata.drop_all()
    Base.metadata.create_all()
    print('models created')

if __name__ == '__main__':
    create_db()


