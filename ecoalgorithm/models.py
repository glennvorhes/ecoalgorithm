import sqlalchemy
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .db_connect import db
import json
from uuid import uuid4
from collections import OrderedDict
from abc import abstractmethod

__all__ = ['create_db', 'DbGeneration', 'SpeciesBase']

Base = declarative_base()


class Generation(Base):
    __tablename__ = 'generation'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, index=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, index=True, unique=True, nullable=False)
    gen_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    individuals = relationship('SpeciesBase', backref='generation', order_by="desc(SpeciesBase._success)")
    """
    :type: list[SpeciesBase]
    """

    def __init__(self, individual_list):
        """

        :param individual_list:
        :type individual_list: list[SpeciesBase]
        :return:
        """

        # last_gen = db.sess.query(DbGeneration.gen_num).order_by(sqlalchemy.desc(DbGeneration.gen_num)).first()
        #
        # if last_gen is None or last_gen[0] is None:
        #     self.gen_num = 1
        # else:
        #     self.gen_num = last_gen[0] + 1
        # db.sess.add(self)
        #
        #
        # for ind in individual_list:
        #     if ind.new_to_db:
        #         db.sess.add(SpeciesBase(self.gen_num, ind))
        #
        # db.sess.commit()

    __table_args__ = {'sqlite_autoincrement': True}


def _breed(individual_1, individual_2):
    """

    :param individual_1:
    :param individual_2:
    :type individual_1: SpeciesBase
    :type individual_2: SpeciesBase
    :return:
    :rtype: list[SpeciesBase]
    """
    assert type(individual_1) is type(individual_2)

    if not individual_1.is_mature:
        raise AssertionError("individual 1 is not mature")

    if not individual_2.is_mature:
        raise AssertionError("individual 2 is not mature")

    if not individual_1.is_alive:
        raise AssertionError("individual 1 is not alive")

    if not individual_2.is_alive:
        raise AssertionError("individual 2 is not alive")

    out_list = []
    """
    :type: list[SpeciesBase]
    """
    offspring_count = individual_1.get_offspring_count()

    while len(out_list) < offspring_count:
        new_ind = individual_1.mate(individual_2)
        new_ind._parent1_id = individual_1.guid
        new_ind._parent2_id = individual_2.guid
        out_list.append(new_ind)

    return out_list


class SpeciesBase(Base):
    __tablename__ = 'individual'
    _uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    _guid = sqlalchemy.Column(sqlalchemy.String(36), index=True, nullable=False)
    _gen_num = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey(Generation.gen_num),
        nullable=False
    )
    _class_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    _success = sqlalchemy.Column(sqlalchemy.Float)
    _parent1_id = sqlalchemy.Column(sqlalchemy.String(36))
    _parent2_id = sqlalchemy.Column(sqlalchemy.String(36))
    _kwargs = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    _alive = sqlalchemy.Column(sqlalchemy.String(1), nullable=False, default='T')

    _offspring_count = 5

    __table_args__ = (
        sqlalchemy.Index('ix_gen_success', '_gen_num', '_success'),
        {'sqlite_autoincrement': True},
    )

    @classmethod
    def get_offspring_count(cls):
        """
        get the number of offspring produced by this species
        :return: the number of offspring returned by breed
        :rtype: int
        """
        return cls._offspring_count

    @classmethod
    def set_offspring_count(cls, new_count):
        """
        Set the number of offspring produced by this species
        :param new_count: new offspring count
        :type new_count: int
        :return:
        """
        if new_count < 2:
            raise Exception('must produce 2 or more offspring')
        cls._offspring_count = new_count

    @classmethod
    def validate_class(cls):
        ind1 = cls()
        ind2 = cls()

        ind1.mature()
        ind2.mature()

        assert ind1._success_set
        assert ind2._success_set

        if not ind1.is_alive:
            ind1.success = 10

        if not ind2.is_alive:
            ind2.success = 10

        progeny = _breed(ind1, ind2)

        assert len(progeny) == ind1.get_offspring_count()

        print("class '{0}' successfully verified".format(ind1.class_name))
        return True

    def __init__(self):
        if self._uid is None:
            self._guid = str(uuid4())
            self._gen_num = None
            self._class_name = self.class_name
            self._parent1_id = None
            self._parent2_id = None
            self._kwargs = json.dumps(self.params)
            self._success = None
            self._alive = 'T'

            self._success_set = False
        else:
            self._set_attributes(**json.loads(self._kwargs))

            self._success_set = True

    def update_params(self):
        self._kwargs = json.dumps(self.params)

    @abstractmethod
    def mature(self):
        """
        mature the individual
        """
        pass

    def mutate(self):
        """
        optional - apply random mutation
        """
        pass

    @abstractmethod
    def mate(self, other_individual):
        """

        :param other_individual:
        :type other_individual: self.__class__
        :return:
        :rtype: SpeciesBase
        """
        pass

    def _set_attributes(self, **kwargs):
        """
        set the public attributes given a kwarg dict

        :param kwargs:
        :type kwargs: dict[str, object]
        """
        for k, v in kwargs.items():
            if k in self.__dict__ and not k.startswith('_'):
                self.__setattr__(k, v)

        for k in [ky for ky in self.__dict__.keys() if not ky.startswith('_')]:
            try:
                assert self.__getattribute__(k) is not None
            except AssertionError:
                raise AssertionError('Attribute \'{0}\' not defined by constructor in class \'{1}\''.format(
                    k, self.class_name
                ))

    @property
    def guid(self):
        return self._guid

    @property
    def params(self):
        """
        Get the object parameters represented as a dictionary

        :return:
        """

        ordered_keys = [k for k in self.__dict__.keys() if not k.startswith('_')]
        ordered_keys.sort()

        params = OrderedDict()

        for k in ordered_keys:
            params[k] = self.__getattribute__(k)

        return params

    @property
    def class_name(self):
        """
        Get the class name

        :return: class name
        :rtype: str
        """
        return self.__class__.__name__

    @property
    def gen_num(self):
        """

        :return:
        :rtype: int|None
        """

        return self._gen_num

    @gen_num.setter
    def gen_num(self, gen):
        """

        :param gen: the generation
        :type gen: int
        :return:
        """

        if self._gen_num is None:
            self._gen_num = gen

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, success):
        self._success_set = True
        self._success = success
        self._alive = 'T' if success is not None else 'F'

    @property
    def is_mature(self):
        return self._success_set

    @property
    def is_alive(self):
        return self._alive == 'T'

    @classmethod
    def get_by_guid(cls, guid):
        """

        :param guid:
        :type guid: str|None
        :return:
        :rtype: SpeciesBase
        """
        if guid is None:
            return None

        ind = db.sess.query(cls).filter(cls._guid == guid).first()

        if not ind:
            return None

        ind.__class__ = cls
        ind.__init__()
        return ind

    @property
    def parent1(self):
        """

        :return:
        :rtype: SpeciesBase
        """
        return self.get_by_guid(self._parent1_id)

    @property
    def parent2(self):
        """

        :return:
        :rtype: SpeciesBase
        """
        return self.get_by_guid(self._parent2_id)


def create_db():
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)

if __name__ == '__main__':
    create_db()
