from pathlib import Path
from unittest import TestCase
import contextlib
import os
import tempfile
import wolk


def make_fs(root, *args, **kwargs):
    root = Path(root)

    for a in args:
        (root / a).write_text(a)

    for k, v in kwargs.items():
        if isinstance(v, str):
            (root / k).write_text(v)
        elif isinstance(v, dict):
            d = os.path.join(root, k)
            os.mkdir(d)
            make_fs(d, **v)
        elif isinstance(v, (list, tuple)):
            assert all(isinstance(i, str) for i in v)
            make_fs(root, **{i: i for i in v})


@contextlib.contextmanager
def temp_fs(*args, **kwargs):
    with tempfile.TemporaryDirectory() as td:
        make_fs(td, *args, **kwargs)
        yield td


class TestWolk(TestCase):
    def test_simple(self):
        with temp_fs('a', 'b', 'c', '.not') as td:
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
