import platform

from .base import (Base,
                   Parameter,
                   Plain,
                   factory)

if platform.python_implementation() != 'PyPy':
    from .base import Overloaded
