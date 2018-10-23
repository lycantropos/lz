from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)
from typing import (Any,
                    Callable)

from lz.curry import (Curry,
                      curry)
from lz.signatures.hints import (MethodDescriptorType,
                                 WrapperDescriptorType)
import pytest


def test_basic(built_in_function: BuiltinFunctionType,
               class_: type,
               function: FunctionType,
               method: MethodType,
               method_descriptor: MethodDescriptorType,
               wrapper_descriptor: WrapperDescriptorType) -> None:
    built_in_function_result = curry(built_in_function)
    class_result = curry(class_)
    function_result = curry(function)
    method_result = curry(method)
    method_descriptor_result = curry(method_descriptor)
    wrapper_descriptor_result = curry(wrapper_descriptor)

    assert isinstance(built_in_function_result, Curry)
    assert isinstance(class_result, Curry)
    assert isinstance(function_result, Curry)
    assert isinstance(method_result, Curry)
    assert isinstance(method_descriptor_result, Curry)
    assert isinstance(wrapper_descriptor_result, Curry)


def test_call(callable_: Callable[..., Any]) -> None:
    result = curry(callable_)

    assert (not result.signature.has_unset_parameters()
            or result() == result)
