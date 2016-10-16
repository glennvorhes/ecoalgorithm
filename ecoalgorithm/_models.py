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

from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count

urls = [
    'http://www.python.org',
    'http://www.python.org/about/',
    'http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html',
    'http://www.python.org/doc/',
    'http://www.python.org/download/',
    'http://www.python.org/getit/',
    'http://www.python.org/community/',
    'https://wiki.python.org/moin/',
    'http://planet.python.org/',
    'https://wiki.python.org/moin/LocalUserGroups',
    'http://www.python.org/psf/',
    'http://docs.python.org/devguide/',
    'http://www.python.org/community/awards/'
    # etc..
]

# # Make the Pool of workers
# pool = ThreadPool(4)
# # Open the urls in their own threads
# # and return the results
# results = pool.map(urllib2.urlopen, urls)
# #close the pool and wait for the work to finish
# pool.close()
# pool.join()

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

        assert len(self._ind_list) > 1
        assert type(female) is type(self._ind_list[0])

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


def _breed(female: 'SpeciesBase', male: 'SpeciesBase'):
    """

    :param female:
    :param male:
    :type female: SpeciesBase
    :type male: SpeciesBase
    :return:
    :rtype: list[SpeciesBase]
    """
    assert type(female) is type(male)

    if not female.is_mature:
        raise AssertionError("individual 1 is not mature")

    if not male.is_mature:
        raise AssertionError("individual 2 is not mature")

    if not female.is_alive:
        raise AssertionError("individual 1 is not alive")

    if not male.is_alive:
        raise AssertionError("individual 2 is not alive")

    out_list = []
    """
    :type: list[SpeciesBase]
    """
    offspring_count = female.get_offspring_count()

    while len(out_list) < offspring_count:
        new_ind = male.mate(female)
        new_ind._parent1_id = female.guid
        new_ind._parent2_id = male.guid
        out_list.append(new_ind)

    return out_list


def mature_individual(ind: 'SpeciesBase'):
    assert ind.class_name != SpeciesBase.__name__
    if not ind.is_mature:
        ind.mature()


class Generation(Base):
    __tablename__ = 'generation'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, index=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, index=True, unique=True, nullable=False)
    gen_time = sqlalchemy.Column(sqlalchemy.DateTime)
    mod_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    _individuals = relationship(
        'SpeciesBase',
        enable_typechecks=False,
        backref='generation',
        order_by="desc(SpeciesBase._success)"
    )
    """
    :type: list[SpeciesBase]
    """

    __table_args__ = {'sqlite_autoincrement': True}

    @classmethod
    def get_current_generation_number(cls) -> int or None:

        last = db.sess.query(cls.gen_num).order_by(sqlalchemy.desc(cls.gen_num)).first()
        return None if last is None else last[0]

    def __init__(self, species_set: Set[type], picker_power=2):
        """
        create a new generation

        """

        self._next_generation = None
        """
        :type: Generation
        """

        self._picker_power = picker_power

        if self.uid is None:
            self.gen_time = self.mod_time = datetime.utcnow()
            the_generation_number = self.get_current_generation_number()
            self.gen_num = 1 if the_generation_number is None else the_generation_number + 1

        self._species_set = species_set
        """
        :type: set[type]
        """

        self._species_lookup = {}
        """
        :type: dict[str, type]
        """

        for c in self._species_set:
            if c.__name__ == SpeciesBase.__name__:
                raise Exception('Cannot add Species base to set')
            self._species_lookup[c.__name__] = c

        self._all_species_picker = IndividualPicker(self.individuals, self._picker_power)

        self._by_species_picker = {
            k: IndividualPicker(
                [ind for ind in self.individuals if ind.class_name == k],
                power=self._picker_power
            ) for k in self._species_lookup.keys()}
        """
        :type: Dict[str, IndividualPicker]
        """

        self._next_gen_individuals = []
        """
        :type: List[SpeciesBase]
        """

    def add_individuals(self, new_individuals: List['SpeciesBase'] or SpeciesBase) -> Set[type]:

        if self._next_generation is not None:
            raise Exception('cannot add more individuals after the next generation is created')

        if type(new_individuals) is not list:
            new_individuals = [new_individuals]

        self._individuals.extend(new_individuals)

        for ind in new_individuals:
            assert ind.class_name != 'SpeciesBase'
            if not ind.is_mature:
                ind.mature()

            self._species_set.add(ind.__class__)

        self.__init__(self._species_set, self._picker_power)

        return self._species_set

    def populate_next_generation(self, max_population: int = 100, keep_all: bool = True):
        if keep_all:
            for class_name, picker in self._by_species_picker.items():
                if picker.has_two_alive:
                    female = picker.pick_female()
                    male = picker.pick_male(female)
                    # print(male, female)
                    progeny = _breed(female, male)
                    # print(progeny[0].class_name)
                    if len(progeny) > 2:
                        progeny = progeny[:2]
                    self._next_gen_individuals.extend(progeny)
                else:
                    # create two new individuals using the class constructor
                    self._next_gen_individuals.append(self._species_lookup[class_name]())
                    self._next_gen_individuals.append(self._species_lookup[class_name]())

        if not self._all_species_picker.has_two_alive and not keep_all:
            """
            No successful individuals
            """
            exit()

        if not self._all_species_picker.has_two_alive:
            while len(self._next_gen_individuals) < max_population:
                for c in self._species_set:
                    self._next_gen_individuals.append(c())

        while len(self._next_gen_individuals) < max_population:
            female = self._all_species_picker.pick_female()

            species_picker = self._by_species_picker[female.class_name]

            if species_picker.has_two_alive:
                male = species_picker.pick_male(female)

                self._next_gen_individuals.extend(_breed(female, male))

        if len(self._next_gen_individuals) > max_population:
            self._next_gen_individuals = self._next_gen_individuals[:max_population]

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

    @property
    def best_individual(self) -> 'SpeciesBase' or None:
        return self._all_species_picker.best_individual

    @property
    def best_success(self) -> float or None:
        best_ind = self.best_individual

        return None if best_ind is None else best_ind.success

    @property
    def individuals(self) -> List['SpeciesBase']:

        for ind in self._individuals:
            if ind.class_name == SpeciesBase.__name__:
                ind.__class__ = self._species_lookup[ind.db_class_name]
                ind.__init__()

        return self._individuals

    @property
    def next_generation(self):
        if self._next_generation is None:
            multi_thread = True

            if len(self._next_gen_individuals) == 0:
                raise AssertionError('Next generation not yet populated')

            # for ind in self._next_gen_individuals:
            #     print(ind.success)

            # TODO compare performance with single thread
            if multi_thread:
                pool = ThreadPool(cpu_count())
                pool.map(mature_individual, self._next_gen_individuals)
                pool.close()
                pool.join()
            else:
                for ind in self._next_gen_individuals:
                    ind.mature()

            # for ind in self._next_gen_individuals:
            #     print(ind.success)

            self._next_generation = Generation(self._species_set, self._picker_power)
            self._next_generation.add_individuals(self._next_gen_individuals)
            self._next_generation.save()

        return self._next_generation


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

    _validated = False

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

        if cls._validated:
            return True

        ind1 = cls()
        ind2 = cls()

        ind1.mature()
        ind2.mature()

        assert ind1.is_mature
        assert ind2.is_mature

        if not ind1.is_alive:
            ind1.success = 10

        if not ind2.is_alive:
            ind2.success = 10

        progeny = _breed(ind1, ind2)

        assert len(progeny) == cls._offspring_count

        for p in progeny:
            try:
                assert p.class_name == cls.__name__
            except AssertionError:
                raise AssertionError('mate must return offspring of the same class: {0} returned {1}'.format(
                    cls.__name__, p.class_name
                ))

        print("class '{0}' successfully verified".format(ind1.class_name))

        cls._validated = True
        return cls._validated

    @classmethod
    def cls(cls):
        return cls

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
        checked by property is_in_db

        Initialize the object normally

        If the uid exists, the object is already persisted to the database and
        therefore has the _kwargs column populuated.  These are used to set the
        default random attributes to those such that the instance matches what
        exists in the database.

        Pretty neat!

        """
        if not self.is_in_db:
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
                # TODO add some checking to assure serializable types
                pass
                # assert self.__getattribute__(k) is not None
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
    def _is_base_class(self) -> bool:
        return self.__class__.__name__ == SpeciesBase.__name__

    @property
    def class_name(self) -> str:
        """
        Get the class name

        :return: class name
        :rtype: str
        """
        if self._is_base_class:
            return SpeciesBase.__name__
        else:
            return self._class_name

    @property
    def db_class_name(self) -> str:
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

    @property
    def is_in_db(self):
        return self.__uid is not None


def create_db():
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)


if __name__ == '__main__':
    create_db()
