from uuid import uuid1
from collections import OrderedDict
__author__ = 'glenn'


class Individual(object):
    """
    The base class for individuals
    """
    _offspring_count = 5

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

    def __init__(self, success=None, **kwargs):
        """
        Constructor

        :param success:
        :type success: float|None
        :param kwargs: kwargs
        :type kwargs: dict
        """
        self.success = None
        self.guid = str(uuid1())

        if success is not None:
            self.success = success

        if 'success' in kwargs:
            del kwargs['success']

        for k, v in kwargs.items():
            if k in self.__dict__:
                self.__setattr__(k, v)

    def mature(self):
        """
        mature the individual
        """
        if type(self) == Individual:
            raise NotImplementedError('not implemented')

    def mutate(self):
        """
        apply random mutation
        """
        if type(self) == Individual:
            raise NotImplementedError('not implemented')

    def mate(self, other_individual):
        """

        :param other_individual:
        :return:
        :rtype: self.__class__
        """
        raise NotImplementedError('not implemented')

    def __str__(self):
        out_string = self.__class__.__name__ + '\n'
        out_string += '\tsuccess={0}\n'.format(self.success)
        out_string += '\tguid={0}\n'.format(self.guid)

        ordered_keys = [k for k in self.__dict__.keys()]
        ordered_keys.sort()

        for k in ordered_keys:
            if k in ('success', 'guid', 'offspring'):
                continue
            out_string += '\t{0}={1}\n'.format(k, self.__getattribute__(k))

        return out_string

    def __repr__(self):
        out_str = self.__class__.__name__ + '('
        ordered_keys = [k for k in self.__dict__.keys()]
        ordered_keys.sort()

        k_v_list = list()

        k_v_list.append('success={0}'.format(self.success))

        for k in ordered_keys:
            if k in ('success', 'guid', 'offspring'):
                continue
            k_v_list.append('{0}={1}'.format(k, self.__getattribute__(k)))

        out_str += ', '.join(k_v_list) + ')'

        return out_str

    def params(self):

        ordered_keys = [k for k in self.__dict__.keys()]
        ordered_keys.sort()

        params = OrderedDict()

        for k in ordered_keys:
            if k in ['guid', 'success']:
                continue
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

