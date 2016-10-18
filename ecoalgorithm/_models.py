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

from . import _helpers

__all__ = ['create_db', 'DbGeneration', 'SpeciesBase']

Base = declarative_base()


class SpeciesBase(Base):
    __tablename__ = 'individual'
    __uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    _guid = sqlalchemy.Column(sqlalchemy.String(36), index=True, nullable=False)
    _gen_num = sqlalchemy.Column(
        sqlalchemy.INTEGER,
        sqlalchemy.ForeignKey('generation.gen_num', ondelete="CASCADE"),
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

        if not issubclass(cls, SpeciesBase):
            raise AssertionError("'{0}' is not subclass of {1}".format(
                cls.__name__, SpeciesBase.__name__
            ))

        ind1 = cls()
        ind2 = cls()

        ind1.mature()
        ind2.mature()

        if not ind1.is_mature or not ind2.is_mature:
            raise AssertionError("'success' property not set in {0} class mature method".format(cls.__name__))

        if not ind1.is_alive:
            ind1.success = 10

        if not ind2.is_alive:
            ind2.success = 10

        progeny = _helpers.breed(ind1, ind2)

        assert len(progeny) == cls._offspring_count

        for p in progeny:
            try:
                assert p.class_name == cls.__name__
            except AssertionError:
                raise AssertionError('mate must return offspring of the same class: {0} returned {1}'.format(
                    cls.__name__, p.class_name
                ))

        cls._validated = True
        return cls._validated

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
        raise NotImplementedError('mature must be overridden by subclasses')

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
        raise NotImplementedError('mate must be overridden by subclasses')

    def _set_attributes(self, **kwargs: dict):
        """
        set the public attributes given a kwarg dict

        :param kwargs:
        :type kwargs: dict[str, object]
        """
        attributes_set_list = []

        for k, v in kwargs.items():
            if k in self.__dict__ and not k.startswith('_'):
                self.__setattr__(k, v)
                attributes_set_list.append(k)

        public_attributes = [ky for ky in self.__dict__.keys() if not ky.startswith('_')]

        for atr in public_attributes:
            if atr not in public_attributes:
                raise AssertionError("attribute {0} not set from database".format(atr))

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


class Generation(Base):
    __tablename__ = 'generation'
    uid = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True, index=True)
    gen_num = sqlalchemy.Column(sqlalchemy.INTEGER, index=True, unique=True, nullable=False)
    gen_time = sqlalchemy.Column(sqlalchemy.DateTime)
    mod_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow())
    _individuals = relationship(
        SpeciesBase,
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

    def __init__(self, species_set: Set[SpeciesBase.__class__]):
        """
        create a new generation

        """

        self._next_generation = None
        """
        :type: Generation
        """

        if self.uid is None:
            self.gen_time = self.mod_time = datetime.utcnow()
            the_generation_number = self.get_current_generation_number()
            self.gen_num = 1 if the_generation_number is None else the_generation_number + 1

        self._species_set = species_set
        """
        :type: set[SpeciesBase.__class__]
        """

        self._species_lookup = {}
        """
        :type: dict[str, SpeciesBase.__class__]
        """

        for c in self._species_set:
            if c.__name__ == SpeciesBase.__name__:
                raise Exception('Cannot add Species base to set')
            self._species_lookup[c.__name__] = c

        self._all_species_picker = _helpers.IndividualPicker(self.individuals)

        self._by_species_picker = {
            k: _helpers.IndividualPicker(
                [ind for ind in self.individuals if ind.class_name == k]) for k in self._species_lookup.keys()}
        """
        :type: Dict[str, _helpers.IndividualPicker]
        """

        self._next_gen_individuals = []
        """
        :type: List[SpeciesBase]
        """

    def add_individuals(self, new_individuals: List[SpeciesBase] or SpeciesBase) -> Set[type]:

        if self._next_generation is not None:
            raise Exception('cannot add more individuals after the next generation is created')

        if type(new_individuals) is not list:
            new_individuals = [new_individuals]

        self._individuals.extend(new_individuals)

        for ind in new_individuals:
            assert ind.class_name != SpeciesBase.__class__.__name__

            self._species_set.add(ind.__class__)

        _helpers.mature_all(new_individuals)

        self.__init__(self._species_set)

        return self._species_set

    def populate_next_generation(self, max_population, keep_all) -> bool:

        if not self._all_species_picker.has_two_alive and not keep_all:
            """
            No successful individuals
            """
            return False

        if keep_all:
            for class_name, picker in self._by_species_picker.items():
                if picker.has_two_alive:
                    female = picker.pick_female()
                    male = picker.pick_male(female)
                    male.get_offspring_count()
                    progeny = _helpers.breed(female, male)
                    self._next_gen_individuals.extend(progeny)
                else:
                    # create new individuals using the class constructor
                    the_class = self._species_lookup[class_name]
                    for i in range(the_class.get_offspring_count()):
                        self._next_gen_individuals.append(the_class())

        if not self._all_species_picker.has_two_alive:
            while len(self._next_gen_individuals) < max_population:
                for c in self._species_set:
                    self._next_gen_individuals.append(c())

        while len(self._next_gen_individuals) < max_population:
            female = self._all_species_picker.pick_female()

            species_picker = self._by_species_picker[female.class_name]

            if species_picker.has_two_alive:
                male = species_picker.pick_male(female)

                self._next_gen_individuals.extend(_helpers.breed(female, male))

        if len(self._next_gen_individuals) > max_population:
            self._next_gen_individuals = self._next_gen_individuals[:max_population]

        return True

    def save(self):

        if len(self.individuals) == 0:
            raise AssertionError('there must at least one individual in the generation')

        _helpers.mature_all(self.individuals)

        if self.uid is None:
            db.sess.add(self)

        self.mod_time = datetime.utcnow()

        db.sess.commit()

    @property
    def best_individual(self) -> SpeciesBase or None:
        return self._all_species_picker.best_individual

    @property
    def best_success(self) -> float or None:
        best_ind = self.best_individual

        return None if best_ind is None else best_ind.success

    @property
    def summary_short(self):
        best = self.best_individual
        if best:
            return "Generation {0}. Best: {1}, success: {2}\n\t{3}".format(
                self.gen_num, best.class_name, best.success,
                dict(best.params)
            )
        else:
            return "Generation {0}. None Successful".format(
                self.gen_num
            )

    @property
    def summary_long(self):
        out_string = "Generation {0}\n".format(self.gen_num)

        # print(self._by_species_picker)

        best_list = []
        none_list = []

        for k, v in self._by_species_picker.items():
            best = v.best_individual
            if best:
                best_list.append((k, best.success, dict(best.params), v.count_all, v.count_alive, v.count_dead))
            else:
                none_list.append((k, v.count_all, v.count_alive, v.count_dead))

        best_list.sort(key=lambda x: x[1], reverse=True)

        for b in best_list:
            out_string += "\t{0}, success: {1}, {2}\n\t\tPopulation count: {3}, alive: {4}, dead: {5}\n".format(*b)

        for n in none_list:
            out_string += "\t{0}, None Successful\n\t\tPopulation count: {1}, alive: {2}, dead: {3}\n".format(*n)

        return out_string

    @property
    def individuals(self) -> List[SpeciesBase]:

        for ind in self._individuals:
            if ind.class_name == SpeciesBase.__name__:
                try:
                    ind.__class__ = self._species_lookup[ind.db_class_name]
                    ind.__init__()
                except KeyError:
                    raise KeyError('Class {0} not found in species set'.format(ind.db_class_name))

        return self._individuals

    @property
    def next_generation(self):
        if self._next_generation is None:

            if len(self._next_gen_individuals) == 0:
                raise AssertionError('Next generation not yet populated')

            _helpers.mature_all(self._next_gen_individuals)

            self._next_generation = Generation(self._species_set)
            self._next_generation.add_individuals(self._next_gen_individuals)
            self._next_generation.save()

        return self._next_generation


def create_db():
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)


if __name__ == '__main__':
    create_db()
