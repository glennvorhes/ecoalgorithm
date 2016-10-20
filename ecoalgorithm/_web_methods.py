import ecoalgorithm
from ._models import SpeciesBase, Generation
from ._db_connect import db
from ._helpers import printd
import json
from typing import List, Tuple
import sqlalchemy
from collections import defaultdict, OrderedDict
from typing import Dict, List


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

        self._min_gen, self._max_gen = db.sess.query(
            sqlalchemy.func.min(
                Generation.gen_num
            ),
            sqlalchemy.func.max(
                Generation.gen_num
            )
        ).first()

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
    def min_gen(self) -> int:
        return self._min_gen

    @property
    def max_gen(self) -> int:
        return self._max_gen

    @property
    def gen_num(self) -> int:
        return self._gen_num

    @property
    def members(self) -> List[_IndividualInfo]:
        return self._members

    @property
    def best_inds(self) -> List[_IndividualInfo]:
        return self._best_inds


class _AllSummary:

    def __init__(self):
        max_vals = db.sess.query(
            SpeciesBase._gen_num,
            sqlalchemy.func.max(SpeciesBase._success)
        ).group_by(
            SpeciesBase._gen_num
        ).order_by(
            SpeciesBase._gen_num
        ).all()

        self._gen_list = []
        self._max_vals = []

        for m in max_vals:
            self._gen_list.append(m[0])
            self._max_vals.append(m[1])

        max_species_vals = db.sess.query(
            SpeciesBase._class_name,
            sqlalchemy.func.max(SpeciesBase._success)
        ).group_by(
            SpeciesBase._gen_num,
            SpeciesBase._class_name
        ).order_by(
            SpeciesBase._gen_num,
            sqlalchemy.desc(
                SpeciesBase._success
            )
        ).all()

        self._species_vals = defaultdict(list)
        """
        :type: dict[str, list[float or None]]
        """

        for m in max_species_vals:
            self._species_vals[m[0]].append(m[1])

        gen_len = len(self._gen_list)

        for v in self._species_vals.values():
            while len(v) < gen_len:
                v.append(None)

    @property
    def c3_json_str(self):

        out_dict = dict({
            'x': 'x',
            'hide': [],
            'json': {
                'x': self._gen_list,
                'All': self._max_vals
            }
        })

        for k, v in self._species_vals.items():
            out_dict['hide'].append(k)
            out_dict['json'][k] = v

        return json.dumps(out_dict, indent=4)



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


def all_summary() -> _AllSummary:
    gen_count = db.sess.query(Generation).count()

    if gen_count < 2:
        return None
    else:
        return _AllSummary()


__all__ = [individual_summary, generation_summary, all_summary]
