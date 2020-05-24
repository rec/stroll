"""✏️safer: a safer file opener ✏️
"""
import os

__version__ = '0.9.0'
__all__ = ('stroll',)


def stroll(*args, **kwargs):
    return os.path.walk(*args, **kwargs)
