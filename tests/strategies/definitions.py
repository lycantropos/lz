import importlib
import inspect
from functools import partial
from itertools import chain
from types import ModuleType
from typing import (Any,
                    Union)

from tests.utils import flatmap

try:
    from typing import Protocol
except ImportError:
    from typing import _Protocol as Protocol

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
modules_callables_list = list(filter(callable, flatmap(
        to_contents, filter(is_supported, stdlib_modules))))
modules_callables = strategies.sampled_from(modules_callables_list)


def is_not_protocol(class_: type) -> bool:
    return Protocol not in class_.__bases__


classes_list = list(
        filter(is_not_protocol,
               filter(is_supported,
                      filter(inspect.isclass, modules_callables_list))))
classes = strategies.sampled_from(classes_list)
classes_callables_list = list(filter(callable, flatmap(to_contents,
                                                       classes_list)))
classes_callables = strategies.sampled_from(classes_callables_list)
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
partial_callables = callables.map(partial)
