from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)

import pytest

from lz.hints import MethodDescriptorType
from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def function() -> FunctionType:
    return find(strategies.functions)


@pytest.fixture(scope='function')
def built_in_function() -> BuiltinFunctionType:
    return find(strategies.built_in_functions)


@pytest.fixture(scope='function')
def method() -> MethodType:
    return find(strategies.methods)


@pytest.fixture(scope='function')
def method_descriptor() -> MethodDescriptorType:
    return find(strategies.methods_descriptors)