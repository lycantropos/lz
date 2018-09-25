import importlib
from functools import singledispatch
from operator import methodcaller
from types import ModuleType
from typing import Any

from . import catalog
from .functional import compose
from .hints import Namespace
from .iterating import flatmapper


@singledispatch
def factory(object_: Any) -> Namespace:
    return object_


@factory.register(catalog.Path)
def from_module_path(object_: catalog.Path) -> Namespace:
    return factory(importlib.import_module(str(object_)))


@factory.register(ModuleType)
def from_module(object_: ModuleType) -> Namespace:
    return dict(vars(object_))


merge = compose(dict,
                flatmapper(methodcaller('items')))
