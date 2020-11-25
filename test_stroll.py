from pathlib import Path
from unittest import TestCase
from unittest import skipIf
import os
import stroll as _stroll
import tdir

IS_TRAVIS = os.getenv('TRAVIS', '').lower().startswith('t')
skip_if_travis = skipIf(IS_TRAVIS, 'Test does not work in travis')


def stroll(top, **kwargs):
    return [str(i) for i in _stroll(top, **kwargs)]


@tdir('a', 'b', 'c', '.not')
class TestStroll(TestCase):
    def test_simple_relative(self):
        actual = stroll('.', relative=True)
        expected = ['a', 'b', 'c']
        assert actual == expected

    def test_simple(self):
        actual = stroll('.')
        expected = ['a', 'b', 'c']
        assert actual == expected

    def test_python(self):
        root = Path(__file__).parent

        actual = [str(i) for i in _stroll.python_source(root, relative=True)]
        expected = ['setup.py', 'stroll.py', 'test_stroll.py']
        assert actual == expected

    def test_error(self):
        with self.assertRaises(TypeError) as m:
            stroll([1, 2, 3])
        expected = 'expected str, bytes or os.PathLike object, not int'
        assert m.exception.args[0] == expected


@tdir('top', s1=['a', 'b', 'c'], s2=['one', 'two'])
class TestStroll2(TestCase):
    def test_complex(self):
        actual = stroll('.')
        expected = ['top', 's1/a', 's1/b', 's1/c', 's2/one', 's2/two']
        assert actual == expected

    def test_complex2(self):
        actual = _stroll(('s1', 's2'), relative=True)
        actual = [(str(r), str(d)) for r, d in actual]
        expected = [
            ('s1', 'a'),
            ('s1', 'b'),
            ('s1', 'c'),
            ('s2', 'one'),
            ('s2', 'two'),
        ]
        assert actual == expected

    def test_topdown(self):
        actual = stroll('.', topdown=True)
        expected = ['top', 's1/a', 's1/b', 's1/c', 's2/one', 's2/two']
        assert actual == expected

    def test_complex_unsorted(self):
        actual = set(stroll(('s1', 's2'), sort=False))
        expected = {'s1/a', 's1/b', 's1/c', 's2/one', 's2/two'}
        assert actual == expected


class TestError(TestCase):
    def test_error(self):
        with self.assertRaises(FileNotFoundError) as m:
            stroll("doesn't-exist-at-all")
        expected = '[Errno 2] No such directory: doesn\'t-exist-at-all'
        assert str(m.exception) == expected

    def test_errors(self):
        with self.assertRaises(FileNotFoundError) as m:
            stroll('XXXX,YYYY')
        expected = '[Errno 2] No such directories: XXXX,YYYY'
        assert str(m.exception) == expected

    def test_ignore_errors(self):
        actual = stroll('XXXX,YYYY', ignore_missing_roots=True)
        expected = []
        assert actual == expected

    @tdir(top=['a', 'b', 'c'])
    def test_ignore_errors2(self):
        actual = stroll('XXXX,top,YYYY', ignore_missing_roots=True)
        expected = ['top/a', 'top/b', 'top/c']
        assert actual == expected


@tdir(
    'top',
    a=('foo.py', 'bar.py', '__init__.py', 'README.md'),
    b=('gong.py', 'bong.py', '__init__.py', 'notes.txt'),
)
class TestSuffix(TestCase):
    def test_python(self):
        actual = stroll('.', suffix='.py')
        expected = [
            'a/__init__.py',
            'a/bar.py',
            'a/foo.py',
            'b/__init__.py',
            'b/bong.py',
            'b/gong.py',
        ]
        assert actual == expected

    def test_include(self):
        actual = stroll('.', include='*o*', suffix='.py')
        expected = ['a/foo.py', 'b/bong.py', 'b/gong.py']
        assert actual == expected


@tdir(
    'top',
    a=dict(foo='bar', aa=dict(one='1', two=dict(doh='re'))),
    b=dict(oom='2', dd=dict(een='1', twee=dict(een=dict(two=dict(drie='f'))))),
)
class TestStrollTopDown(TestCase):
    @skip_if_travis
    def test_not_topdown_dirs(self):
        # TODO: why doesn't this work on Travis?!
        actual = stroll('.', topdown=False, directories=True)
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
        actual = stroll('.', topdown=True, directories=True)
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
        actual = stroll('.', topdown=False)
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
        actual = stroll('.', topdown=True)
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
        actual = stroll('.', exclude='a/|top/', include='*/drie')
        expected = ['b/dd/twee/een/two/drie']
        assert expected == actual


@tdir(
    'top',
    a=dict(foo='bar', aa=dict(one='1', two=dict(doh='re'))),
    b=dict(oom='2', dd=dict(een='1', twee=dict(een=dict(two=dict(drie='f'))))),
)
class TestMultipleRoots(TestCase):
    def test_multiple(self):
        expected = [
            'a/foo',
            'a/aa/one',
            'a/aa/two/doh',
            'b/oom',
            'b/dd/een',
            'b/dd/twee/een/two/drie',
        ]
        for roots in 'a,b', ['a', 'b'], (i for i in 'ab'):
            actual = stroll(roots)
            assert actual == expected


class TestParamCount(TestCase):
    def test_simple(self):
        count = _stroll._param_count

        assert count(lambda: 0) == 0
        assert count(lambda a: 0) == 1
        assert count(lambda a, b: 0) == 2
        assert count(lambda a, b, c: 0) == 3
        with self.assertRaises(ValueError):
            count(lambda a, b, c, d: 0)

    def test_var(self):
        count = _stroll._param_count

        assert count(lambda *e: 0) == 3
        assert count(lambda a, *e: 0) == 3
        assert count(lambda a, b, *e: 0) == 3
        assert count(lambda a, b, *e: 0) == 3
        assert count(lambda a, b, c, *e: 0) == 3
        with self.assertRaises(ValueError):
            count(lambda a, b, c, d, *e: 0)

    def test_default(self):
        count = _stroll._param_count

        assert count(lambda a=1: 0) == 1
        assert count(lambda a=1, b=2: 0) == 2
        assert count(lambda a=1, b=2, c=3: 0) == 3
        assert count(lambda a=1, b=2, c=3: 0) == 3
        assert count(lambda a=1, b=2, c=3, d=4: 0) == 3


class TestInv(TestCase):
    def test_inv(self):
        a = 1, 2, 3
        fn = _stroll.inv(a.__contains__)

        for i in (1, 2, 7):
            assert (i in a) == (not fn(i))
