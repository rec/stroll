🚶 stroll: a better os.path.walk 🚶
-------------------------------------

Drop-in substitute for ``os.path.walk()`` with additional features:

* Handles Unix-style globs or "star notation" like \*.py

* Walks over multiple roots

* Yields ``pathlib.Path()`` instead of ``str``

* Yields full absolute paths by default

* Can exclude or include files flexibly by pattern or function

* Raises ``FileNotFoundError`` if a root directory doesn't exist, instead
  of silently doing nothing like ``os.walk`` does (bad feature!).

* Excludes dotfiles by default

* Includes two functions for ignoring generated files in a Python project:

  * The Python build, test and release cycle tend to leave genereted files in
    places like build/ or __pycache__, and usually you want to ignore these

  * ``stroll.python_source()`` iterates over Python source files

  * ``stroll.python()`` iterates over all source files in a Python project

  * The files and directories that are ignored are:
      * files or directories that start with a .
      * .egg-info/ and __pycache__/
      * build/, dist/ and htmlcov/ at the top level only

API
===

``stroll()``
~~~~~~~~~~~~

.. code-block:: python

  stroll(
       topdown=True,
       onerror=None,
       followlinks=False,
       include=None,
       exclude=<function dotfile at 0x103e2f510>,
       directories=False,
       relative=False,
       with_root=None,
       sort=True,
       suffix=None,
       separator=',',
       ignore_missing_roots=False,
  )

(`stroll.py, 56-221 <https://github.com/rec/stroll/blob/master/stroll.py#L56-L221>`_)

Directory tree generator that improves on ``os.walk``.

For each directory in ``roots``, walk through each file in each
subdirectory and yield a Path to that file.  Ignores dotfiles by default.

EXAMPLE

.. code-block:: python

    import stroll

    for f in stroll('~/foo:~/bar'):
        if f.suffix == '.txt':
            print(f)

    for f in stroll.python_source('/code/project'):
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
    A list of patterns that files must match.

    Patterns can either be a Unix-style match string,
    or a Python callable which returns True if the file matches

  exclude
    A list of patterns that files cannot match (and will skip).

    Patterns can either be a Unix-style match string,
    or a Python callable which returns True if the file matches.

  directories
    If True, both files and directories are yielded.
    If False, the default, only files are yielded

  relative
    If True, file paths are relative to the root they were found in.
    If False, the default, absolute paths are generated.

  with_root
    If True, pairs looking like (root, filepath) are generated.
    If False, just file paths are generated.
    If None, the default, pairs are generated only if there is more than
    one root *and* relative paths are selected.

  sort
    If True, files or subdirectories are generated in sorted order.
    If False, the default, files or subdirectories are generated in
    whatever order the operating system gives them, which might be
    sorted anyway

  suffix
     If None, the default, there is no suffix matching.  Note that
     ``include`` and ``exclude`` might match suffixes independently.

  ignore_missing_roots
    If True, root directories that do not exist are silently skipped.
    If False, the default, all roots are checked for existence before
    any files are generated.

``stroll.python()``
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  stroll.python(
       roots,
       topdown=True,
       onerror=None,
       followlinks=False,
       include=None,
       exclude=(<function dotfile at 0x103e2f510>, <function match_root at 0x103ea51e0>, <function match_suffix at 0x103ea5268>, <function match at 0x103ea52f0>),
       directories=False,
       relative=False,
       with_root=None,
       sort=True,
       suffix=None,
       separator=',',
       ignore_missing_roots=False,
  )

Iterate over a Python project, skipping generated files

``stroll.python_source()``
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  stroll.python_source(
       roots,
       topdown=True,
       onerror=None,
       followlinks=False,
       include='*.py',
       exclude=(<function dotfile at 0x103e2f510>, <function match_root at 0x103ea51e0>, <function match_suffix at 0x103ea5268>, <function match at 0x103ea52f0>),
       directories=False,
       relative=False,
       with_root=None,
       sort=True,
       suffix=None,
       separator=',',
       ignore_missing_roots=False,
  )

Iterate over \*.py files in a Python project, skipping generated files

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2020-11-06T21:24:41.363753)
