"""Better directory tree generator"""
from pathlib import Path
import fnmatch
import functools
import inspect
import os
import re
import xmod

__version__ = '0.9.0'
__all__ = 'wolk', 'inv', 'python', 'python_source'


def dotfile(filename):
    return filename.startswith('.')


@xmod
def wolk(
    top,
    topdown=True,
    onerror=None,
    followlinks=False,
    include=None,
    exclude=dotfile,
    directories=False,
    relative=False,
    with_root=None,
    sort=True,
):
    inc = include and _resolve(include)
    exc = _resolve(exclude or ())

    roots = [top] if isinstance(top, (str, Path)) else top

    if relative and with_root is None:
        with_root = len(roots) != 1

    for root in roots:
        walk = os.walk(root, topdown, onerror, followlinks)
        root = Path(root)

        for directory, sub_dirs, files in walk:
            if sort:
                sub_dirs.sort()
                files.sort()

            directory = Path(directory)

            def results(files):
                for f in files:
                    f = directory / f
                    if relative:
                        f = f.relative_to(root)
                    if with_root:
                        yield str(root), str(f)
                    else:
                        yield str(f)

            def accept(file):
                args = file, directory, root
                return not exc(*args) and (inc is None or inc(*args))

            yield from results(f for f in files if accept(f))

            if topdown or directories:
                subs = (f for f in sub_dirs if accept(f + '/'))
                if topdown:
                    sub_dirs[:] = subs
                    subs = sub_dirs
                if directories:
                    yield from results(subs)


def _resolve(r):
    def wrap(match):
        if isinstance(match, str):
            return wrap_string(match)

        assert callable(match)
        return wrap_callable(match)

    def wrap_string(match):
        fmatch = re.compile(fnmatch.translate(match)).match

        def wrapped(filename, directory, root):
            return fmatch(os.path.join(directory, filename))

        return wrapped

    def wrap_callable(match):
        p = _param_count(match)
        if p == 3:
            return match
        return lambda *args: match(*args[:p])

    if isinstance(r, str) or callable(r):
        r = (r,)

    matchers = [wrap(f) for f in r]
    return lambda *a: any(m(*a) for m in matchers)


def matcher(f):
    @functools.wraps(f)
    def outer(*args):
        @functools.wraps(f)
        def inner(filename, directory, root):
            return f(filename, directory, root, *args)

        return inner

    return outer


@matcher
def match(filename, directory, root, *files):
    return filename in files


@matcher
def match_root(filename, directory, root, *files):
    return directory == root and filename in files


@matcher
def match_suffix(filename, directory, root, *suffixes):
    return filename.endswith(suffixes)


EXCLUDE_PYTHON = (
    dotfile,
    match_root('build/', 'dist/', 'htmlcov/'),
    match_suffix('.egg-info/'),
    match('__pycache__/'),
)


python = functools.partial(wolk, exclude=EXCLUDE_PYTHON)
python_source = functools.partial(wolk, include='*.py', exclude=EXCLUDE_PYTHON)


def _param_count(fn, n=3):
    i = -1

    for i, p in enumerate(inspect.signature(fn).parameters.values()):
        if p.kind in (p.KEYWORD_ONLY, p.VAR_KEYWORD):  # pragma: no cover

            return i

        if p.kind is p.VAR_POSITIONAL:
            return n

        if i >= n:
            if p.default is not p.empty:
                return n
            raise ValueError('Patterns can have at most %s arguments' % n)

    return min(i + 1, n)


def inv(fn):
    @functools.wraps(fn)
    def wrapped(*args):
        return not fn(*args)

    return wrapped
