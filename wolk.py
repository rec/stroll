"""
🚶 wolk: a better os.path.walk 🚶
-------------------------------------

Drop-in substitute for ``os.path.walk()`` with additional features:

* Walks over multiple roots

* Yields ``pathlib.Path()`` and not ``str``

* Yields full absolute paths by default

* Can exclude or include files flexibly by pattern or function

* Excludes dotfiles by default

* Two special patterns to match all files in a Python project,
  or all Python sound files, are included

The last one is useful because Python tends to leave all sorts of copies
of your code in directories like ``build/``, ``dist/`` or ``*.egg/``.
"""
from pathlib import Path
import fnmatch
import functools
import inspect
import os
import re
import xmod

__version__ = '0.9.3'
__all__ = 'wolk', 'inv', 'python', 'python_source'

FILE_SEPARATOR = '|'


def dotfile(filename):
    return filename.startswith('.')


@xmod
def wolk(
    roots,
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
    """
    Directory tree generator that improves on ``os.walk``.

    For each directory in ``roots``, walk through each file in each
    subdirectory and yield a Path to that file.  Ignores dotfiles by default.

    EXAMPLE
    ^^^^^^^

    .. code-block:: python

        import wolk

        for f in wolk('~/foo:~/bar'):
            if f.suffix == '.txt':
                print(f)

        for f in wolk.python_source('/code/project'):
            assert f.suffix == '.py'


    ARGUMENTS
      topdown
        If optional arg ``topdown`` is true or not specified, the ``Path`` to a
        directory is generated before any of its subdirectories - directories
        are generated top-down.

        If ``topdown`` is false, the Path to a directory is generated after all
        of its subdirectories - directories are generated bottom up.

      onerror
        By default errors from the os.scandir() call are ignored.  If
        optional arg 'onerror' is specified, it should be a function; it
        will be called with one argument, an OSError instance.  It can
        report the error to continue with the walk, or raise the exception
        to abort the walk.  Note that the filename is available as the
        filename attribute of the exception object.

      followlinks
        By default, os.walk does not follow symbolic links to subdirectories on
        systems that support them.  In order to get this functionality, set the
        optional argument 'followlinks' to true.

        Caution:  if you pass a relative pathname for top, don't change the
        current working directory between resumptions of walk.  walk never
        changes the current directory, and assumes that the client doesn't
        either.


      include

      exclude

      directories

      relative

      with_root

      sort



    """
    inc = _resolve(include, match_on_empty=True)
    exc = _resolve(exclude, match_on_empty=False)

    if isinstance(roots, str):
        roots = roots.split(':')
    elif isinstance(roots, Path):
        roots = [roots]
    else:
        try:
            len(roots)
        except Exception:
            roots = list(roots)

    if relative and with_root is None:
        with_root = len(roots) != 1

    for root in roots:
        root = Path(root).expanduser()
        walk = os.walk(str(root), topdown, onerror, followlinks)

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
                        yield root, f
                    else:
                        yield f

            def accept(is_dir, file):
                a = file, directory, root
                return inc(is_dir, *a) and not exc(is_dir, *a)

            yield from results(f for f in files if accept(False, f))

            if topdown or directories:
                subs = (f for f in sub_dirs if accept(True, f + '/'))
                if topdown:
                    sub_dirs[:] = subs
                    subs = sub_dirs
                if directories:
                    yield from results(subs)


def _resolve(pattern, match_on_empty):
    matchers = [], []

    def wrap(match):
        if callable(match):
            p = _param_count(match)
            fn = match if p == 3 else lambda *args: match(*args[:p])
            matchers[0].append(fn)
            matchers[1].append(fn)
        else:
            fmatch = re.compile(fnmatch.translate(match))

            def wrapped(filename, directory, root):
                return fmatch.match(os.path.join(directory, filename))

            is_dir = match.endswith(os.path.sep)
            matchers[is_dir].append(wrapped)

    if callable(pattern):
        pattern = (pattern,)
    elif isinstance(pattern, str):
        pattern = pattern.split(FILE_SEPARATOR)

    for m in pattern or ():
        wrap(m)

    if match_on_empty:
        for m in matchers:
            if not m:
                m.append(lambda *a: True)

    def matcher(is_dir, *args):
        return any(m(*args) for m in matchers[is_dir])

    return matcher


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
