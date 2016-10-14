import sqlalchemy
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from ecoalgorithm.db_connect import db
import json
from uuid import uuid4
from collections import OrderedDict
from abc import abstractmethod
from typing import List, Dict, Set
import numpy as np
from numpy.random import choice

__all__ = ['create_db', 'DbGeneration', 'SpeciesBase']

Base = declarative_base()


class IndividualPicker:

    def __init__(self, ind_list: List['SpeciesBase'], power=2):
        """
        Make a chooser function in a closure

        :param ind_list: the items to be potentially picked
        :type ind_list: list[SpeciesBase]
        :param power: the power to which the picker decay function should be, use exp if not provided
        :type power: float|None
        """
        for j in ind_list:
            assert j.is_mature

        self._ind_list = [i for i in ind_list if i.is_alive]

        self._ind_list.sort(key=lambda x: x.success, reverse=True)
        self._wgt = np.linspace(-1, 0, len(self._ind_list) + 1)

        self._wgt *= -1

        self._wgt **= power
        self._wgt = self._wgt[:-1]
        self._wgt /= np.sum(self._wgt)

    def pick_female(self) -> 'SpeciesBase':
        """
        Make weighted selection

        :return: the selection
        :rtype: SpeciesBase
        """
        return choice(self._ind_list, p=self._wgt)

    def pick_male(self, female) -> 'SpeciesBase':

        ix_female = self._ind_list.index(female)

        no_female = [self._ind_list[i] for i in range(len(self._ind_list)) if i != ix_female]
        no_female_weight = [self._wgt[i] for i in range(len(self._wgt)) if i != ix_female]
        no_female_weight /= np.sum(no_female_weight)

        return choice(no_female, p=no_female_weight)

    @property
    def num_alive(self):
        return len(self._ind_list)

    @property
    def has_two_alive(self) -> bool:
        return len(self._ind_list) > 1

    @property
    def best_individual(self) -> 'SpeciesBase':
        if len(self._ind_list) > 0:
            return self._ind_list[0]
        else:
            return None


class Generation(Base):
    __tablename__ = 'generation'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, index=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, index=True, unique=True, nullable=False)
    gen_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    mod_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    individuals = relationship(
        'SpeciesBase',
        enable_typechecks=False,
        backref='generation',
        order_by="desc(SpeciesBase._success)"
    )
    """
    :type: list[SpeciesBase]
    """

    @classmethod
    def get_current_generation_number(cls) -> int or None:

        last = db.sess.query(cls.gen_num).order_by(sqlalchemy.desc(cls.gen_num)).first()
        return None if last is None else last[0]

    def __init__(self):
        """
        create a new generation

        """

        if self.uid is None:
            print('here')
            the_generation_number = self.get_current_generation_number()
            self.gen_num = 1 if the_generation_number is None else the_generation_number + 1

        self._species_set = set()
        """
        :type: set[type]
        """

        self._species_lookup = {}
        """
        :type: dict[str, type]
        """

        self._all_species_picker = IndividualPicker([])

        self._by_species_picker = {'a': IndividualPicker([])}
        """
        :type: Dict[str, IndividualPicker]
        """

        self._next_generation = []
        """
        :type: List[SpeciesBase]
        """

    def add_individuals(self, new_individuals: List['SpeciesBase']) -> Set[type]:

        for ind in new_individuals:
            assert ind.class_name != 'SpeciesBase'
            if not ind.is_mature:
                ind.mature()

            self._species_set.add(ind.__class__)

        self.individuals.extend(new_individuals)
        self._update_species_lookup()
        self._update_stats()

        return self._species_set

    def _update_stats(self, picker_power=2):
        self._all_species_picker = IndividualPicker(self.individuals, power=picker_power)

        self._by_species_picker.clear()

        for k in self._species_lookup.keys():
            self._by_species_picker[k] = IndividualPicker(
                [ind for ind in self.individuals if ind.class_name == k],
                power=picker_power
            )

        # print(self._all_species_picker.pick_female())
        # print(self._species_lookup)
        # print(self._by_species_picker)

    def _update_species_lookup(self):
        self._species_lookup.clear()

        for c in self._species_set:
            self._species_lookup[c.__name__] = c

    def fix_species_classes(self, species_set):
        """
        convert species into what they should be based on a class lookup

        used after retrieval from the database as all come as SpeciesBase

        :param species_set:
        :return:
        """

        try:
            self._species_set
        except AttributeError:
            self.__init__()

        for c in species_set:
            self._species_set.add(c)

        self._update_species_lookup()

        for ind in self.individuals:
            ind.__class__ = self._species_lookup[ind.class_name]
            ind.__init__()

        self._update_stats()

    def make_next_generation(self, max_population: int = 100, keep_all: bool = True):
        pass

    def save(self):
        if len(self.individuals) < 2:
            raise AssertionError('there must be at least two individuals in the generation')

        for ind in self.individuals:
            if not ind.is_mature:
                ind.mature()

        if self.uid is None:
            db.sess.add(self)

        self.mod_time = datetime.utcnow()

        db.sess.commit()

        if self.uid is None:
            db.sess.add()

    @property
    def best_individual(self) -> 'SpeciesBase' or None:
        return self._all_species_picker.best_individual

    @property
    def best_success(self) -> float or None:
        best_ind = self.best_individual

        return None if best_ind is None else best_ind.success

    __table_args__ = {'sqlite_autoincrement': True}


def _breed(individual_1: 'SpeciesBase', individual_2: 'SpeciesBase'):
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
    __uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    _guid = sqlalchemy.Column(sqlalchemy.String(36), index=True, nullable=False)
    _gen_num = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey(Generation.gen_num, ondelete="CASCADE"),
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
    def get_offspring_count(cls) -> int:
        """
        get the number of offspring produced by this species
        :return: the number of offspring returned by breed
        :rtype: int
        """
        return cls._offspring_count

    @classmethod
    def set_offspring_count(cls, new_count: int):
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
    def validate_class(cls) -> bool:
        """
        Little class method to let the creator of subclasses know that it checks out

        :return:
        """
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
        """
        The the init method of subclasses is called in two contexts

        First, as one would expect by instantiating a new instance.

        Atlernatively, objects retrieved from the database are always of
        type SpeciesBase.  However, using a class lookup based on the attribute
        from the database,  the class can be altered by means of the following

        species_instance.__class__ = <subclass>
        species instance.__init__()

        The call to init adds the subclass specfic attributes as created
        by the subclass constructor followed by the call to the super
        constructor.

        Note the fall through.

        If the uid is None, that means it is not yet in the database

        Initialize the object normally

        If the uid exists, the object is already persisted to the database and
        therefore has the _kwargs column populuated.  These are used to set the
        default random attributes to those such that the instance matches what
        exists in the database.

        Pretty neat!

        """
        if self.__uid is None:
            self._guid = str(uuid4())
            self._gen_num = None
            self._class_name = self.__class__.__name__
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
    def mate(self, other_individual: 'SpeciesBase') -> 'SpeciesBase':
        """

        :param other_individual:
        :type other_individual: self.__class__
        :return:
        :rtype: SpeciesBase
        """
        pass

    def _set_attributes(self, **kwargs: dict):
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
    def guid(self) -> str:
        return self._guid

    @property
    def params(self) -> dict:
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
    def class_name(self) -> str:
        """
        Get the class name

        :return: class name
        :rtype: str
        """
        return self._class_name

    @property
    def gen_num(self) -> int or None:
        """

        :return:
        :rtype: int|None
        """

        return self._gen_num

    @gen_num.setter
    def gen_num(self, gen: int):
        """

        :param gen: the generation
        :type gen: int
        :return:
        """

        if self._gen_num is None:
            self._gen_num = gen

    @property
    def success(self) -> float or None:
        return self._success

    @success.setter
    def success(self, success: float or None):
        self._success_set = True
        self._success = success
        self._alive = 'T' if success is not None else 'F'

    @property
    def is_mature(self) -> bool:
        return self._success_set

    @property
    def is_alive(self) -> bool:
        return self._alive == 'T'

    @classmethod
    def get_by_guid(cls, guid: str) -> 'SpeciesBase':
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
    def parent1(self) -> 'SpeciesBase':
        """

        :return:
        :rtype: SpeciesBase
        """
        return self.get_by_guid(self._parent1_id)

    @property
    def parent2(self) -> 'SpeciesBase':
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
