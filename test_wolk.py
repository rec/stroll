from pathlib import Path
from unittest import TestCase
import tdir
import wolk


class TestWolk(TestCase):
    def test_simple(self):
        with tdir.tdir('a', 'b', 'c', '.not') as td:
            actual = sorted(wolk.wolk(td, relative=True))
            expected = ['a', 'b', 'c']
            assert actual == expected

    def test_python(self):
        actual = sorted(wolk.python_source(Path(__file__).parent))
        expected = ['setup.py', 'test_wolk.py', 'wolk.py']
        assert actual == expected


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
