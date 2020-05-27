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

The last one is really useful because Python tends to leave all sorts of copies
of your code in directories like ``build/``, ``dist/`` or ``*.egg/``.
