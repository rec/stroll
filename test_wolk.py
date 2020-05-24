from unittest import TestCase
import wolk


class TestParamCount(TestCase):
    def test_simple(self):
        count = wolk._param_count

        assert count(lambda: 0) == 0
        assert count(lambda a: 0) == 1
        assert count(lambda a, b: 0) == 2
        assert count(lambda a, b, c: 0) == 3
        with self.assertRaises(ValueError):
            count(lambda a, b, c, d: 0)

    def test_var(self):
        count = wolk._param_count

        assert count(lambda *e: 0) == 3
        assert count(lambda a, *e: 0) == 3
        assert count(lambda a, b, *e: 0) == 3
        assert count(lambda a, b, *e: 0) == 3
        assert count(lambda a, b, c, *e: 0) == 3
        with self.assertRaises(ValueError):
            count(lambda a, b, c, d, *e: 0)

    def test_default(self):
        count = wolk._param_count

        assert count(lambda a=1: 0) == 1
        assert count(lambda a=1, b=2: 0) == 2
        assert count(lambda a=1, b=2, c=3: 0) == 3
        assert count(lambda a=1, b=2, c=3: 0) == 3
        assert count(lambda a=1, b=2, c=3, d=4: 0) == 3
