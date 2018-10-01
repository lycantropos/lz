import importlib
from functools import singledispatch
from types import ModuleType
from typing import Any

from . import catalog
from .hints import Namespace


@singledispatch
def factory(object_: Any) -> Namespace:
    return object_


@factory.register(catalog.Path)
def from_module_path(object_: catalog.Path) -> Namespace:
    return factory(importlib.import_module(str(object_)))


@factory.register(ModuleType)
def from_module(object_: ModuleType) -> Namespace:
    return dict(vars(object_))
