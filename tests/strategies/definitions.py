import importlib
import inspect
import pickle
from functools import partial
from types import ModuleType
from typing import (Any,
                    Callable,
                    Iterable,
                    List,
                    Union)

from hypothesis import strategies
from paradigm._core.catalog import path_to_string
from paradigm._core.discovery import supported_stdlib_modules_paths
from paradigm.base import signature_from_callable

from lz.hints import Domain
from tests.utils import flatmap

stdlib_modules_names_list = [path_to_string(module_path)
                             for module_path in supported_stdlib_modules_paths]


def is_supported(value: Any) -> bool:
    try:
        signature = signature_from_callable(value)
    except (TypeError, ValueError):
        return False
    else:
        try:
            pickle.dumps(signature)
        except pickle.PicklingError:
            return False
        else:
            return True


def to_contents(module_or_type: Union[ModuleType, type]) -> Iterable[Any]:
    return vars(module_or_type).values()


def to_filtered(predicate: Callable[[Domain], bool],
                values: Iterable[Domain]) -> List[Domain]:
    return [value for value in values if predicate(value)]


stdlib_modules = [importlib.import_module(module_name)
                  for module_name in stdlib_modules_names_list]
modules_callables_list = list(filter(callable,
                                     flatmap(to_contents, stdlib_modules)))
modules_callables = (strategies.sampled_from(stdlib_modules_names_list)
                     .map(importlib.import_module)
                     .map(to_contents)
                     .map(partial(filter, callable))
                     .map(list)
                     .filter(bool)
                     .flatmap(strategies.sampled_from))
classes = (strategies.sampled_from(stdlib_modules_names_list)
           .map(importlib.import_module)
           .map(to_contents)
           .map(partial(filter, inspect.isclass))
           .map(list)
           .filter(bool)
           .flatmap(strategies.sampled_from))
classes_callables = (classes
                     .map(to_contents)
                     .map(partial(filter, callable))
                     .map(list)
                     .filter(bool)
                     .flatmap(strategies.sampled_from))
callables = (modules_callables | classes_callables).filter(is_supported)
partial_callables = callables.map(partial)
