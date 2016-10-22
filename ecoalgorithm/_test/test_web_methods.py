import ecoalgorithm
from ecoalgorithm._test.test_ecosystem import build_example
from unittest import TestCase
from ecoalgorithm import start_web_server
from unittest import TestCase
from .._models import Generation, SpeciesBase
from .._helpers import printd
from .. import _web_methods as web
import os
from .._db_connect import db
from .example_species import get_species_set, get_some_inds



class TestWebMethods(TestCase):

    # def test_test(self):
    #     build_example()

    def setUp(self):
        ecoalgorithm.config.db_path = os.path.join(os.getcwd(), 'test_dbs', 'web_test.db')

    def test_get_ind_info(self):
        pass
        # ind_summ = web.individual_summary('db61c619-4785-441d-9d7c-678ccba3078a')
        # self.assertGreaterEqual(len(ind_summ.siblings), 10)


    def test_get_gen(self):
        eco = ecoalgorithm.Ecosystem(get_species_set(), get_some_inds(), use_existing=False)
        eco.run(2)
        gen_sum = web.generation_summary(2)
        # get_species_set, get_some_inds
        self.assertIsNotNone(gen_sum)

    def test_get_summary(self):
        db.clear_db()
        all_summ = web.all_summary()
        self.assertIsNone(all_summ)

        # printd(gen_sum)
    #     print(gen_sum.members)

        # ind = SpeciesBase.get_by_guid('4bae7a6d-fb12-4011-8871-f3238a6923f5')

    # def test_get_ind_info_no_parent(self):
    #     ind_summ = web.individual_summary('4fdfb6dd-19fe-44e7-868a-7aae752c6d9f')
    #
    # def test_get_ind_no_success(self):
    #     ind_summ = web.individual_summary('e5d83652-1de0-4cd3-ae3c-4c32f4a9a8a2')
