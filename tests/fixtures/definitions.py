from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)
from typing import (Any,
                    Callable)

import pytest
from paradigm.hints import (MethodDescriptorType,
                            WrapperDescriptorType)

from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def built_in_function() -> BuiltinFunctionType:
    return find(strategies.built_in_functions)


@pytest.fixture(scope='function')
def callable_() -> Callable[..., Any]:
    return find(strategies.callables)


@pytest.fixture(scope='function')
def class_() -> type:
    return find(strategies.classes)


@pytest.fixture(scope='function')
def function() -> FunctionType:
    return find(strategies.functions)


@pytest.fixture(scope='function')
def method() -> MethodType:
    return find(strategies.methods)


@pytest.fixture(scope='function')
def method_descriptor() -> MethodDescriptorType:
    return find(strategies.methods_descriptors)


@pytest.fixture(scope='function')
def wrapper_descriptor() -> WrapperDescriptorType:
    return find(strategies.methods_descriptors)
