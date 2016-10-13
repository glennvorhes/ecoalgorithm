from uuid import uuid4
from collections import OrderedDict
from abc import abstractmethod
import json
__author__ = 'glenn'


class SpeciesBase(object):
    """
    The base class for individuals
    """
    _offspring_count = 5



    @classmethod
    def validate_species(cls):

        error_messages = ''

        # validate constructor
        new_ind0 = cls()

        new_ind0 = cls(success=10)
        if new_ind0.success != 10:
            error_messages += 'Something wrong with success definition for class: {0}\n'.format(new_ind0.class_name)

        new_ind0 = cls(success=10, **{})

        new_ind1 = cls()
        new_ind2 = cls()

        assert new_ind1.parent1 is None
        assert new_ind1.parent2 is None

        new_ind1.mature()

        if new_ind1.success is None:
            error_messages += 'Mature method not appropriately defined for class: {0}\n'.format(new_ind1.class_name)

        new_ind3 = new_ind1.mate(new_ind2)
        new_ind3.parent1 = new_ind1.guid
        new_ind3.parent2 = new_ind2.guid

        if not isinstance(new_ind3, cls):
            error_messages += 'Mate method not not return a new individual of class: {0}\n'.format(new_ind1.class_name)

        type(new_ind1)(new_ind1.success, **new_ind1.params)

        try:
            json.dumps(new_ind1.params)
        except TypeError:
            error_messages += 'class \'{0}\' has attributes that are not serializable\n\t{1}\n'.format(
                new_ind1.class_name, new_ind1.params)

        if len(error_messages) > 0:
            raise AssertionError(error_messages)
        else:
            print(new_ind1.class_name + " class successfully validated")

    def __init__(self, success=None, **kwargs):
        """
        Constructor

        :param success:
        :type success: float|None
        :param kwargs: kwargs
        :type kwargs: dict
        """
        self._success = success if success is not None else None

        self._guid = str(uuid4())
        self._new_to_db = True

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

        self._parent1 = None
        self._parent2 = None
        self._is_alive = True



    @abstractmethod
    def mature(self):
        """
        mature the individual
        """
        pass

    @abstractmethod
    def mutate(self):
        """
        apply random mutation
        """
        pass

    @abstractmethod
    def mate(self, other_individual):
        """

        :param other_individual:
        :return:
        :rtype: self.__class__
        """
        pass

    def die(self):
        self._success = None
        self._is_alive = False

    def __str__(self):
        out_string = self.__class__.__name__ + '\n'
        out_string += '\tguid={0}\n'.format(self.guid)
        out_string += '\tsuccess={0}\n'.format(self.success)

        ordered_keys = [k for k in self.__dict__.keys() if not k.startswith('_')]
        ordered_keys.sort()

        for k in ordered_keys:
            out_string += '\t{0}={1}\n'.format(k, self.__getattribute__(k))

        return out_string

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
    def success(self):
        """
        Get success value

        :return: success
        :rtype: float|None
        """
        return self._success

    @property
    def parent1(self):
        """
        Parent 1 identifier

        :return: parent 1 id
        :rtype: str|None
        """
        return self._parent1

    @parent1.setter
    def parent1(self, parent):
        """
        Parent 1 identifier setter, not to be used in client code

        :param parent: the parent id
        :type parent: str|None
        """
        self._parent1 = parent

    @property
    def parent2(self):
        """
        Parent 2 identifier

        :return: parent 1 id
        :rtype: str|None
        """
        return self._parent2

    @parent2.setter
    def parent2(self, parent):
        """
        Parent 2 identifier setter, not to be used in client code

        :param parent: the parent id
        :type parent: str|None
        """
        self._parent2 = parent

    @property
    def guid(self):
        """
        the unique identifier of the individual

        :return: guid
        :rtype: str
        """
        return self._guid

    @guid.setter
    def guid(self, g):
        """
        used internally to set the guid of individuals retrieved from the database, not to be used in client code

        :param g: the guid
        :type g: str
        """
        self._guid = g
        self._new_to_db = False

    @property
    def new_to_db(self):
        """
        used internally check if the individual is new/should be added to the database or if it is a new individual

        :return:
        :rtype: bool
        """
        return self._new_to_db

    @property
    def is_alive(self):
        """
        Check if the individual made it through maturation

        :return:
        """

        return self._is_alive
