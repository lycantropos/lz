import importlib
import inspect
import pickle
from functools import partial
from types import ModuleType
from typing import (Any,
                    Iterable,
                    Union)

from hypothesis import strategies
from paradigm._core.catalog import path_to_string
from paradigm._core.discovery import supported_stdlib_modules_paths
from paradigm.base import signature_from_callable

from tests.utils import flatmap

stdlib_modules_names = [path_to_string(module_path)
                        for module_path in supported_stdlib_modules_paths]
stdlib_modules = [importlib.import_module(module_name)
                  for module_name in stdlib_modules_names]


def is_supported(value: Any) -> bool:
    try:
        signature = signature_from_callable(value)
        pickle.dumps(signature)
    except (ValueError, pickle.PicklingError):
        return False
    else:
        return True


def to_contents(module_or_type: Union[ModuleType, type]) -> Iterable[Any]:
    return vars(module_or_type).values()


modules_callables_list = list(filter(callable,
                                     flatmap(to_contents, stdlib_modules)))
modules_callables = strategies.sampled_from(modules_callables_list)
classes_list = list(filter(inspect.isclass, modules_callables_list))
classes_callables_list = list(filter(callable,
                                     flatmap(to_contents, classes_list)))
classes_callables = strategies.sampled_from(classes_callables_list)
callables = (modules_callables | classes_callables).filter(is_supported)
partial_callables = callables.map(partial)
