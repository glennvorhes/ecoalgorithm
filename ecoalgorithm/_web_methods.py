import ecoalgorithm
from ._models import SpeciesBase, Generation
from ._db_connect import db
from collections import OrderedDict
from ._helpers import printd
import json
from typing import List, Tuple
import sqlalchemy


# SpeciesBase = ecoalgorithm.SpeciesBase


def something():
    # print(ecoalgorithm.db)
    pass


def _get_children_count(guid):
    return db.sess.query(SpeciesBase).filter(
        sqlalchemy.or_(
            SpeciesBase._mother_id == guid,
            SpeciesBase._father_id == guid
        )
    ).count()


class _IndividualInfo:
    def __init__(self, guid, success, class_name):
        self.guid = guid
        self.success = success
        self.class_name = class_name
        self.child_count = _get_children_count(guid)


class _IndividualSummary:
    def __init__(self, ind: SpeciesBase):

        self._siblings = []
        self._children = []
        self._params = []

        self._class_name = ind.db_class_name
        self._gen_num = ind.gen_num
        self._sucess = ind.success

        parms = json.loads(ind._kwargs)
        for k, v in parms.items():
            self._params.append((k, v))

        self._params.sort(key=lambda x: x[0])

        mother = ind.mother
        if mother is not None:
            self._mother = _IndividualInfo(mother.guid, mother.success, mother.db_class_name)

        father = ind.father
        if father is not None:
            self._father = _IndividualInfo(father.guid, father.success, mother.db_class_name)

        if mother is not None and father is not None:
            sibs = db.sess.query(SpeciesBase._guid, SpeciesBase._success, SpeciesBase._class_name).filter(
                sqlalchemy.or_(
                    SpeciesBase._mother_id == self.mother.guid,
                    SpeciesBase._father_id == self.father.guid,
                    SpeciesBase._father_id == self.mother.guid,
                    SpeciesBase._mother_id == self.father.guid
                )
            ).order_by(sqlalchemy.desc(SpeciesBase._success)).all()

            for s in sibs:
                self._siblings.append(_IndividualInfo(*s))

        chil = db.sess.query(SpeciesBase._guid, SpeciesBase._success, SpeciesBase._class_name).filter(
            sqlalchemy.or_(
                SpeciesBase._mother_id == ind.guid,
                SpeciesBase._father_id == ind.guid
            )
        ).order_by(sqlalchemy.desc(SpeciesBase._success)).all()

        for c in chil:
            self._children.append(_IndividualInfo(*c))

    @property
    def gen_num(self):
        return self._gen_num

    @property
    def class_name(self) -> str or None:
        return self._class_name

    @property
    def success(self) -> float or None:
        return self._sucess

    @property
    def params(self) -> List[Tuple[str, object]]:
        return self._params

    @property
    def mother(self) -> _IndividualInfo or None:
        return self._mother

    @property
    def father(self) -> _IndividualInfo or None:
        return self._father

    @property
    def siblings(self) -> List[_IndividualInfo]:
        return self._siblings

    @property
    def children(self) -> List[_IndividualInfo]:
        return self._children


class _GenerationSummary:
    def __init__(self, gen_num: int):
        self._gen_num = gen_num

        mems = db.sess.query(SpeciesBase._guid, SpeciesBase._success, SpeciesBase._class_name).filter(
            SpeciesBase._gen_num == gen_num).order_by(
            sqlalchemy.desc(SpeciesBase._success)
        ).all()

        self._members = [_IndividualInfo(*m) for m in mems]


        max_vals = db.sess.query(
            SpeciesBase._guid,
            sqlalchemy.func.max(SpeciesBase._success),
            SpeciesBase._class_name
        ).filter(
            SpeciesBase._gen_num == gen_num
        ).group_by(SpeciesBase._class_name).order_by(
            sqlalchemy.desc(SpeciesBase._success)
        ).all()

        self._best_inds = [_IndividualInfo(*m) for m in max_vals]

    @property
    def gen_num(self) -> int:
        return self._gen_num

    @property
    def members(self) -> List[_IndividualInfo]:
        return self._members

    @property
    def best_inds(self) -> List[_IndividualInfo]:
        return self._best_inds


def individual_summary(guid: str) -> _IndividualSummary or None:
    ind = SpeciesBase.get_by_guid(guid)
    if ind is None:
        return None
    else:
        return _IndividualSummary(ind)


def generation_summary(gen_num: int) -> _GenerationSummary or None:
    g = db.sess.query(Generation.gen_num).filter(Generation.gen_num == gen_num).first()

    if g is None:
        return None
    else:
        return _GenerationSummary(gen_num)


__all__ = [individual_summary]
