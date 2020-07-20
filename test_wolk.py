from pathlib import Path
from unittest import TestCase
from unittest import skipIf
import os
import tdir
import wolk

IS_TRAVIS = os.getenv('TRAVIS', '').lower().startswith('t')
skip_if_travis = skipIf(IS_TRAVIS, 'Test does not work in travis')


@tdir('a', 'b', 'c', '.not')
class TestWolk(TestCase):
    def test_simple_relative(self):
        actual = list(wolk('.', relative=True))
        expected = ['a', 'b', 'c']
        assert actual == expected

    def test_simple(self):
        actual = list(wolk('.'))
        expected = ['a', 'b', 'c']
        assert actual == expected

    def test_python(self):
        root = Path(__file__).parent

        actual = list(wolk.python_source(root, relative=True))
        expected = ['setup.py', 'test_wolk.py', 'wolk.py']
        assert actual == expected

    def test_error(self):
        with self.assertRaises(TypeError) as m:
            list(wolk([1, 2, 3]))
        expected = 'expected str, bytes or os.PathLike object, not int'
        assert m.exception.args[0] == expected


@tdir('top', s1=['a', 'b', 'c'], s2=['one', 'two'])
class TestWolk2(TestCase):
    def test_complex(self):
        actual = list(wolk('.'))
        expected = ['top', 's1/a', 's1/b', 's1/c', 's2/one', 's2/two']
        assert actual == expected

    def test_complex2(self):
        actual = list(wolk(('s1', 's2'), relative=True))
        expected = [
            ('s1', 'a'),
            ('s1', 'b'),
            ('s1', 'c'),
            ('s2', 'one'),
            ('s2', 'two'),
        ]
        assert actual == expected

    def test_topdown(self):
        actual = list(wolk('.', topdown=True))
        expected = ['top', 's1/a', 's1/b', 's1/c', 's2/one', 's2/two']
        assert actual == expected

    def test_complex_unsorted(self):
        actual = set(wolk(('s1', 's2'), sort=False))
        expected = {'s1/a', 's1/b', 's1/c', 's2/one', 's2/two'}
        assert actual == expected


@tdir(
    'top',
    a=dict(foo='bar', aa=dict(one='1', two=dict(doh='re'))),
    b=dict(oom='2', dd=dict(een='1', twee=dict(een=dict(two=dict(drie='f'))))),
)
class TestWolkTopDown(TestCase):
    @skip_if_travis
    def test_not_topdown_dirs(self):
        # TODO: why doesn't this work on Travis?!
        actual = list(wolk('.', topdown=False, directories=True))
        expected = [
            'a/aa/two/doh',
            'a/aa/one',
            'a/aa/two',
            'a/foo',
            'a/aa',
            'b/dd/twee/een/two/drie',
            'b/dd/twee/een/two',
            'b/dd/twee/een',
            'b/dd/een',
            'b/dd/twee',
            'b/oom',
            'b/dd',
            'top',
            'a',
            'b',
        ]
        assert expected == actual

    def test_topdown_dirs(self):
        actual = list(wolk('.', topdown=True, directories=True))
        expected = [
            'top',
            'a',
            'b',
            'a/foo',
            'a/aa',
            'a/aa/one',
            'a/aa/two',
            'a/aa/two/doh',
            'b/oom',
            'b/dd',
            'b/dd/een',
            'b/dd/twee',
            'b/dd/twee/een',
            'b/dd/twee/een/two',
            'b/dd/twee/een/two/drie',
        ]
        assert expected == actual

    @skip_if_travis
    def test_not_topdown(self):
        actual = list(wolk('.', topdown=False))
        expected = [
            'a/aa/two/doh',
            'a/aa/one',
            'a/foo',
            'b/dd/twee/een/two/drie',
            'b/dd/een',
            'b/oom',
            'top',
        ]
        print(actual)
        assert expected == actual

    def test_topdown(self):
        actual = list(wolk('.', topdown=True))
        expected = [
            'top',
            'a/foo',
            'a/aa/one',
            'a/aa/two/doh',
            'b/oom',
            'b/dd/een',
            'b/dd/twee/een/two/drie',
        ]
        assert expected == actual

    def test_inc_exc(self):
        actual = list(wolk('.', exclude='a/|top/', include='*/drie'))
        expected = ['b/dd/twee/een/two/drie']
        assert expected == actual


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


class TestInv(TestCase):
    def test_inv(self):
        a = 1, 2, 3
        fn = wolk.inv(a.__contains__)

        for i in (1, 2, 7):
            assert (i in a) == (not fn(i))
