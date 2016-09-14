from unittest import TestCase
from test.example_species import Bird, Cat, Fish
from ecoalgorithm.models import DbGeneration
from ecoalgorithm.ecosystem import OneGeneration
from ecoalgorithm import db_connect
from ecoalgorithm import models
from ecoalgorithm.ecosystem import parse_generation

db_conn = db_connect.db


class TestParseGeneration(TestCase):

    def test_parseGen(self):

        out_inds = parse_generation([Bird, Cat, Fish])
        print(out_inds)




