from unittest import TestCase
from eco.ecosystem import _individual_picker
from collections import defaultdict
from collections import OrderedDict

class Test_individual_picker(TestCase):
    def test__pick1(self):
        t = []
        picker_count = OrderedDict()
        for i in range(100):
            t.append(i)
            picker_count[str(i)] = 0

        picker = _individual_picker(t, power=3)

        for i in range(100):
            pick_val = picker()
            picker_count[str(pick_val)] += 1

        for k, v in picker_count.items():
            print('{0}: {1}'.format(k, v))

    def test__pick2(self):
        t = []
        picker_count = OrderedDict()
        for i in range(100):
            t.append(i)
            picker_count[str(i)] = 0

        picker = _individual_picker(t, power=2)

        for i in range(100):
            pick_val = picker()
            picker_count[str(pick_val)] += 1

        for k, v in picker_count.items():
            print('{0}: {1}'.format(k, v))
