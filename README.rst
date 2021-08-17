🚶 stroll: a better os.path.walk 🚶
-------------------------------------

``stroll`` is a drop-in substitute for ``os.path.walk()`` with more features:

* Unix-style globs or "star notation" like \*.py

* Walks over multiple roots

* Calls expanduser to handle paths like ``~/foo.txt``

* Yields ``pathlib.Path()`` instead of ``str``

* Yields full absolute paths by default

* Can exclude or include files flexibly by pattern or function

* Raises ``FileNotFoundError`` if a root directory doesn't exist, instead
  of silently doing nothing like ``os.walk`` does

* Excludes dotfiles by default

* Includes two functions for ignoring generated files in a Python project:

  * The Python build, test and release cycle tend to leave generated files in
    places like ``build/`` or ``__pycache__/``, and usually you want to ignore
    these

  * ``stroll.python_source()`` iterates over Python source files

  * ``stroll.python()`` iterates over all source files in a Python project

  * The files and directories that are ignored are:
      * files or directories that start with a ``.``
      * ``.egg-info/`` and ``__pycache__/``
      * ``build/``, ``dist/`` and ``htmlcov/`` at the top level only

API
===

``stroll()``
~~~~~~~~~~~~

.. code-block:: python

  stroll(
       roots='.',
       topdown=True,
       onerror=None,
       followlinks=False,
       include=None,
       exclude=<function dotfile at 0x10c6e47b8>,
       directories=False,
       relative=False,
       with_root=None,
       sort=True,
       suffix=None,
       separator=',',
       ignore_missing_roots=False,
  )

(`stroll.py, 59-228 <https://github.com/rec/stroll/blob/master/stroll.py#L59-L228>`_)

Directory walker that improves on ``os.walk()``.

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
  roots
    Either a list or tuple of strings, or a single string that is split
    using ``separator`` (defaults to ``,``, the comma).

  topdown (argument to ``os.walk``)
    If optional arg ``topdown`` is true or not specified, the ``Path`` to a
    directory is generated before any of its subdirectories - directories
    are generated top-down.

    If ``topdown`` is false, the Path to a directory is generated after all
    of its subdirectories - directories are generated bottom up.

  onerror (argument to ``os.walk``)
    By default errors from the ``os.scandir()`` call are ignored.  If
    optional arg ``onerror`` is specified, it should be a function; it
    will be called with one argument, an OSError instance.  It can
    report the error to continue with the walk, or raise the exception
    to abort the walk.  Note that the filename is available as the
    filename attribute of the exception object.

  followlinks (argument to ``os.walk``)
    By default, ``os.walk()`` does not follow symbolic links to
    subdirectories on systems that support them.  In order to get this
    functionality, set the optional argument ``followlinks`` to true.

    Caution:  if you pass a relative pathname for top, don't change the
    current working directory between resumptions of walk.  ``os.walk()``
    never changes the current directory, and assumes that the client
    doesn't either.

  include
    A list of patterns that files must match.

    Patterns can either be a Unix-style match string,
    or a Python callable which returns ``True`` if the file matches

  exclude
    A list of patterns that files cannot match (and will skip).

    Patterns can either be a Unix-style match string,
    or a Python callable which returns ``True`` if the file matches.

  directories
    If true, both files and directories are yielded.
    If false, the default, only files are yielded

  relative
    If true, file paths are relative to the root they were found in.
    If false, the default, absolute paths are generated.

  with_root
    If true, pairs looking like (root, filepath) are generated.
    If ``False``, just file paths are generated.
    If ``None``, the default, pairs are generated only if there is more than
    one root *and* relative paths are selected.

  sort
    If true, files or subdirectories are generated in sorted order.
    If false, the default, files or subdirectories are generated in
    whatever order the operating system gives them, which might be
    sorted anyway

  suffix
     If ``None``, the default, there is no suffix matching.  Note that
     ``include`` and ``exclude`` might match suffixes independently.

  ignore_missing_roots
    If true, root directories that do not exist are silently skipped.
    If false, the default, all roots are checked for existence before
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
       exclude=(<function dotfile at 0x10c6e47b8>, <function match_root at 0x10c754400>, <function match_suffix at 0x10c754488>, <function match at 0x10c754510>),
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
       exclude=(<function dotfile at 0x10c6e47b8>, <function match_root at 0x10c754400>, <function match_suffix at 0x10c754488>, <function match at 0x10c754510>),
       directories=False,
       relative=False,
       with_root=None,
       sort=True,
       suffix=None,
       separator=',',
       ignore_missing_roots=False,
  )

Iterate over \*.py files in a Python project, skipping generated files

(automatically generated by `doks <https://github.com/rec/doks/>`_ on 2020-11-21T15:09:32.268025)
