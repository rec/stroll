from pathlib import Path
import fnmatch
import functools
import inspect
import os
import re

__version__ = '0.9.0'
__all__ = ('wolk',)


def dotfile(filename):
    return filename.startswith('.')


def wolk(
    top,
    topdown=True,
    onerror=None,
    followlinks=False,
    include=None,
    exclude=dotfile,
    directories=False,
    relative=True,
    with_root=None,
):
    inc = include and _resolve(include)
    exc = _resolve(exclude or ())

    roots = [top] if isinstance(top, (str, Path)) else list(top)
    if relative and with_root is None:
        with_root = len(roots) != 1

    for root in roots:
        walk = os.walk(root, topdown, onerror, followlinks)
        for directory, sub_dirs, files in walk:

            def results(files):
                for f in files:
                    f = os.path.join(directory, f)
                    if relative:
                        f = os.path.relpath(f, root)

                    yield (root, f) if with_root else f

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


def match_python(filename, directory, root):
    if filename.endswith('.py'):
        return True

    if not filename.endswith('/'):
        return False

    if directory == root and filename in _PYTHON_ROOT_DIRECTORIES:
        return False

    return not any(filename.endswith(d) for d in _PYTHON_DIR_SUFFIXES)


python = functools.partial(wolk, include=match_python)


def _wrap(matcher):
    if isinstance(matcher, str):
        match = re.compile(fnmatch.translate(matcher)).match

        def wrapped(filename, directory, root):
            return match(os.path.join(directory, filename))

        return wrapped

    if not callable(matcher):
        raise ValueError('Do not understand %s' % matcher)

    p = _param_count(matcher)
    if p == 3:
        return matcher
    return lambda *args: matcher(*args[:p])


def _param_count(fn, n=3):
    i = -1

    for i, p in enumerate(inspect.signature(fn).parameters.values()):
        if p.kind in (p.KEYWORD_ONLY, p.VAR_KEYWORD):
            return i

        if p.kind is p.VAR_POSITIONAL:
            return n

        if i >= n:
            if p.default is not p.empty:
                return n
            raise ValueError('Patterns can have at most %s arguments' % n)

    return min(i + 1, n)


def _resolve(r):
    if isinstance(r, str) or callable(r):
        r = (r,)

    matchers = [_wrap(f) for f in r]
    return lambda *a: all(m(*a) for m in matchers)


def neg(fn):
    @functools.wraps(fn)
    def wrapped(*args):
        return not fn(*args)

    return wrapped


_PYTHON_ROOT_DIRECTORIES = 'build/', 'dist/', 'htmlcov/'
_PYTHON_DIR_SUFFIXES = ('.egg-info/',)
