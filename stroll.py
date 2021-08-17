"""
🚶 stroll: a better os.path.walk 🚶
-------------------------------------

`stroll` is a drop-in substitute for `os.path.walk()` with more features:

* Unix-style globs or "star notation" like \\*.py

* Walks over multiple roots

* Calls expanduser to handle paths like `~/foo.txt`

* Yields `pathlib.Path()` instead of `str`

* Yields full absolute paths by default

* Can exclude or include files flexibly by pattern or function

* Raises `FileNotFoundError` if a root directory doesn't exist, instead
  of silently doing nothing like `os.walk` does

* Excludes dotfiles by default

* Includes two functions for ignoring generated files in a Python project:

  * The Python build, test and release cycle tend to leave generated files in
    places like `build/` or `__pycache__/`, and usually you want to ignore
    these

  * `stroll.python_source()` iterates over Python source files

  * `stroll.python()` iterates over all source files in a Python project

  * The files and directories that are ignored are:
      * files or directories that start with a `.`
      * `.egg-info/` and `__pycache__/`
      * `build/`, `dist/` and `htmlcov/` at the top level only
"""

from pathlib import Path
import fnmatch
import functools
import inspect
import os
import re
import xmod

__version__ = '1.1.0'
__all__ = 'inv', 'python', 'python_source'

FILE_SEPARATOR = ','
_DOKS = {}


def dotfile(filename):
    return filename.startswith('.')


@xmod
def stroll(
    roots='.',
    topdown=True,
    onerror=None,
    followlinks=False,
    include=None,
    exclude=dotfile,
    directories=False,
    relative=False,
    with_root=None,
    sort=True,
    suffix=None,
    separator=FILE_SEPARATOR,
    ignore_missing_roots=False,
):
    """
    Directory walker that improves on `os.walk()`.

    For each directory in `roots`, walk through each file in each
    subdirectory and yield a Path to that file.  Ignores dotfiles by default.

    EXAMPLE

    .. code-block:: python

        import stroll

        # Print all the files in the current directory
        print(*list(stroll()

        for f in stroll('~/foo:~/bar'):
            if f.suffix == '.txt':
                print(f)

        for f in stroll.python_source('/code/project'):
            assert f.suffix == '.py'

    ARGUMENTS
      roots
        Either a list or tuple of strings, or a single string that is split
        using `separator` (defaults to `,`, the comma).

      topdown (argument to `os.walk`)
        If optional arg `topdown` is true or not specified, the `Path` to a
        directory is generated before any of its subdirectories - directories
        are generated top-down.

        If `topdown` is false, the Path to a directory is generated after all
        of its subdirectories - directories are generated bottom up.

      onerror (argument to `os.walk`)
        By default errors from the `os.scandir()` call are ignored.  If
        optional arg `onerror` is specified, it should be a function; it
        will be called with one argument, an OSError instance.  It can
        report the error to continue with the walk, or raise the exception
        to abort the walk.  Note that the filename is available as the
        filename attribute of the exception object.

      followlinks (argument to `os.walk`)
        By default, `os.walk()` does not follow symbolic links to
        subdirectories on systems that support them.  In order to get this
        functionality, set the optional argument `followlinks` to true.

        Caution:  if you pass a relative pathname for top, don't change the
        current working directory between resumptions of walk.  `os.walk()`
        never changes the current directory, and assumes that the client
        doesn't either.

      include
        A list of patterns that files must match.

        Patterns can either be a Unix-style match string,
        or a Python callable which returns `True` if the file matches

      exclude
        A list of patterns that files cannot match (and will skip).

        Patterns can either be a Unix-style match string,
        or a Python callable which returns `True` if the file matches.

      directories
        If true, both files and directories are yielded.
        If false, the default, only files are yielded

      relative
        If true, file paths are relative to the root they were found in.
        If false, the default, absolute paths are generated.

      with_root
        If true, pairs looking like (root, filepath) are generated.
        If `False`, just file paths are generated.
        If `None`, the default, pairs are generated only if there is more than
        one root *and* relative paths are selected.

      sort
        If true, files or subdirectories are generated in sorted order.
        If false, the default, files or subdirectories are generated in
        whatever order the operating system gives them, which might be
        sorted anyway

      suffix
         If `None`, the default, there is no suffix matching.  Note that
         `include` and `exclude` might match suffixes independently.

      ignore_missing_roots
        If true, root directories that do not exist are silently skipped.
        If false, the default, all roots are checked for existence before
        any files are generated.
    """

    def split_file(x, to_path):
        if isinstance(x, Path):
            x = [str(x)]
        elif isinstance(x, str):
            x = x.split(separator)
        if to_path:
            return [Path(i).expanduser() for i in x]
        return list(x)

    roots = split_file(roots, True)
    if not ignore_missing_roots:
        missing = [f for f in roots if not f.exists()]
        if missing:
            d = 'directory' if len(missing) == 1 else 'directories'
            m = separator.join(str(i) for i in missing)
            raise FileNotFoundError(2, 'No such %s: %s' % (d, m))

    inc = _Pattern(include, match_on_empty=True)
    exc = _Pattern(exclude, match_on_empty=False)

    if suffix is None:
        suffixes = None
    else:
        # The empty string means "requires no suffix"
        suffixes = set('' if suffix == '' else split_file(suffix, False))

    if relative and with_root is None:
        with_root = len(roots) != 1

    for root in roots:
        walk = os.walk(str(root), topdown, onerror, followlinks)

        for directory, sub_dirs, files in walk:
            if sort:
                sub_dirs.sort()
                files.sort()

            directory = Path(directory)

            def results(files):
                for f in files:
                    f = directory / f
                    if not suffixes or f.suffix in suffixes:
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


class _Pattern:
    def __init__(self, pattern, match_on_empty):
        self.match_on_empty = match_on_empty
        self.file_matcher, self.dir_matcher = [], []

        def wrap_callable(match):
            p = _param_count(match)
            fn = match if p == 3 else lambda *args: match(*args[:p])
            self.file_matcher.append(fn)
            self.dir_matcher.append(fn)

        def wrap_re(match):
            fmatch = re.compile(fnmatch.translate(match))

            def wrapped(filename, directory, root):
                return fmatch.match(os.path.join(directory, filename))

            if match.endswith(os.path.sep):
                self.dir_matcher.append(wrapped)
            else:
                self.file_matcher.append(wrapped)

        if callable(pattern):
            pattern = (pattern,)

        elif isinstance(pattern, str):
            pattern = pattern.split(FILE_SEPARATOR)

        for m in pattern or ():
            if callable(m):
                wrap_callable(m)
            else:
                wrap_re(m)

    def __call__(self, is_dir, *args):
        matcher = self.dir_matcher if is_dir else self.file_matcher
        if not matcher:
            return self.match_on_empty

        return any(m(*args) for m in matcher)


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
    match_suffix('.egg-info/', '.pyc'),
    match('__pycache__/'),
)

python = functools.partial(stroll, exclude=EXCLUDE_PYTHON)
python_source = functools.partial(
    stroll, include='*.py', exclude=EXCLUDE_PYTHON
)

_DOKS[python] = 'Iterate over a Python project, skipping generated files'
_DOKS[
    python_source
] = 'Iterate over \\*.py files in a Python project, skipping generated files'


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
