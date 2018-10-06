import importlib.abc
import importlib.machinery
import sys
import types
from functools import singledispatch
from types import ModuleType
from typing import Any

from lz.functional import compose
from lz.iterating import (flatten,
                          mapper,
                          sifter)
from . import (catalog,
               dictionaries)
from .hints import Namespace


@singledispatch
def factory(object_: Any) -> Namespace:
    return object_


replacing_modules_names = {
    '_importlib_modulespec': [types.__name__,
                              importlib.abc.__name__,
                              importlib.machinery.__name__]}
if sys.platform == 'win32':
    import nt

    replacing_modules_names['posix'] = [nt.__name__]
to_replacing_modules_names = compose(flatten,
                                     sifter(),
                                     mapper(replacing_modules_names.get))


@factory.register(catalog.Path)
def from_module_path(object_: catalog.Path) -> Namespace:
    modules_names = list(to_replacing_modules_names(object_.parts))
    if modules_names:
        return dictionaries.merge(map(compose(factory,
                                              importlib.import_module),
                                      modules_names))
    return factory(importlib.import_module(str(object_)))


@factory.register(ModuleType)
def from_module(object_: ModuleType) -> Namespace:
    return dict(vars(object_))
