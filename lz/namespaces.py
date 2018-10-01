import importlib
import importlib.abc
import importlib.machinery
import types
from functools import singledispatch
from types import ModuleType
from typing import Any

from . import (catalog,
               dictionaries)
from .functional import compose
from .hints import Namespace


@singledispatch
def factory(object_: Any) -> Namespace:
    return object_


replacements = {'_importlib_modulespec': 'types'}


@factory.register(catalog.Path)
def from_module_path(object_: catalog.Path) -> Namespace:
    parts = map(replacements.get, object_.parts, object_.parts)
    new_path = catalog.Path(*parts)
    if new_path != object_:
        return dictionaries.merge(map(compose(factory,
                                              importlib.import_module),
                                      [types.__name__,
                                       importlib.abc.__name__,
                                       importlib.machinery.__name__]))
    return factory(importlib.import_module(str(new_path)))


@factory.register(ModuleType)
def from_module(object_: ModuleType) -> Namespace:
    return dict(vars(object_))
