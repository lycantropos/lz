import importlib
import inspect
from types import ModuleType
from typing import (Any,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy
from paradigm.definitions import (is_supported,
                                  stdlib_modules_names,
                                  to_contents,
                                  unsupported)
from paradigm.hints import (MethodDescriptorType,
                            WrapperDescriptorType)

stdlib_modules = list(map(importlib.import_module,
                          stdlib_modules_names
                          - unsupported.stdlib_modules_names))
modules = (strategies.sampled_from(stdlib_modules)
           .filter(is_supported))


def flatten_module_or_class(object_: Union[ModuleType, type]
                            ) -> SearchStrategy:
    return strategies.sampled_from(to_contents(object_))


modules_callables = (modules.flatmap(flatten_module_or_class)
                     .filter(callable))
classes = (modules_callables.filter(inspect.isclass)
           .filter(is_supported))
classes_callables = (classes.flatmap(flatten_module_or_class)
                     .filter(callable))
methods = classes_callables.filter(inspect.isfunction)


def is_method_descriptor(object_: Any) -> bool:
    return isinstance(object_, MethodDescriptorType)


methods_descriptors = (classes_callables.filter(is_method_descriptor)
                       .filter(is_supported))


def is_wrapper_descriptor(object_: Any) -> bool:
    return isinstance(object_, WrapperDescriptorType)


wrappers_descriptors = (classes_callables.filter(is_wrapper_descriptor)
                        .filter(is_supported))
functions = modules_callables.filter(inspect.isfunction)
built_in_functions = (modules_callables.filter(inspect.isbuiltin)
                      .filter(is_supported))
callables = (built_in_functions
             | classes
             | functions
             | methods
             | methods_descriptors
             | wrappers_descriptors)
