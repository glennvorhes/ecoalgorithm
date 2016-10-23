import ecoalgorithm
import os
from ecoalgorithm import db, config
from ecoalgorithm._test.example_species import Cat, Dog, Fish, DeadFish, Snake, Racoon, \
    get_some_inds, get_species_set, get_some_inds_len, ExampleSpecies
import multiprocessing

ecoalgorithm.config.db_path = os.path.join(os.path.dirname(__file__), 'test_dbs', 'results.db_446')
ecoalgorithm.config.multithread = False
from ecoalgorithm._helpers import printd
import sqlalchemy
import json

delete_top = True
replace_inds = True

if __name__ == '__main__':
    db.clear_db()
    config.multithread = False

    run_gens = 4

    inds = []
    species_set = {Fish, Cat, Dog}
    species_lookup = {s.__name__: s for s in species_set}

    # TODO fix what happens if there is only one of a species
    for i in range(1):
        inds.append(Cat())
        inds.append(Fish())
        inds.append(Dog())

    eco = ecoalgorithm.Ecosystem(species_set, inds, use_existing=False)
    eco.run(run_gens, ecoalgorithm.ShowOutput.SHORT)

    mn, mx = db.sess.query(
        sqlalchemy.func.max(
            ecoalgorithm.SpeciesBase._success
        ),
        sqlalchemy.func.max(
            ecoalgorithm.SpeciesBase._success
        )
    ).filter(
        ecoalgorithm.SpeciesBase._gen_num == run_gens + 1
    ).first()

    cl = db.sess.query(ecoalgorithm.SpeciesBase._class_name).filter(
        ecoalgorithm.SpeciesBase._success == mx
    ).first()[0]

    new_inds = []

    if delete_top:

        db.sess.query(ecoalgorithm.SpeciesBase).filter(
            sqlalchemy.and_(
                ecoalgorithm.SpeciesBase._class_name == cl,
                ecoalgorithm.SpeciesBase._gen_num == run_gens + 1
            )
        ).delete()

        db.sess.commit()

    if replace_inds:
        bad_succ, bad_guid = db.sess.query(
            ecoalgorithm.SpeciesBase._success,
            ecoalgorithm.SpeciesBase._guid
        ).filter(
            ecoalgorithm.SpeciesBase._gen_num == 1,
        ).order_by(
            ecoalgorithm.SpeciesBase._success
        ).first()

        bad = ecoalgorithm.SpeciesBase.get_by_guid(bad_guid)

        c = species_lookup[cl]
        for i in range(4):
            f = c(**json.loads(bad._kwargs))
            new_inds.append(f)

    printd('restarting')

    eco = ecoalgorithm.Ecosystem(get_species_set(), new_inds)
    eco.run(400, ecoalgorithm.ShowOutput.SHORT, break_threshold=None)
