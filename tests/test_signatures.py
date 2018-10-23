from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)
from typing import (Any,
                    Callable)

from lz import signatures
from lz.signatures.hints import (MethodDescriptorType,
                                 WrapperDescriptorType)


def test_factory(class_: type,
                 function: FunctionType,
                 built_in_function: BuiltinFunctionType,
                 method: MethodType,
                 method_descriptor: MethodDescriptorType,
                 wrapper_descriptor: WrapperDescriptorType) -> None:
    class_result = signatures.factory(class_)
    built_in_function_result = signatures.factory(built_in_function)
    function_result = signatures.factory(function)
    method_result = signatures.factory(method)
    method_descriptor_result = signatures.factory(method_descriptor)
    wrapper_descriptor_result = signatures.factory(wrapper_descriptor)

    assert isinstance(class_result, signatures.Base)
    assert isinstance(built_in_function_result, signatures.Base)
    assert isinstance(function_result, signatures.Base)
    assert isinstance(method_result, signatures.Base)
    assert isinstance(method_descriptor_result, signatures.Base)
    assert isinstance(wrapper_descriptor_result, signatures.Base)


def test_has_unset_parameters(callable_: Callable[..., Any]) -> None:
    result = signatures.factory(callable_)

    assert (not isinstance(result, signatures.Plain)
            or result.has_unset_parameters()
            or all(parameter.has_default
                   for parameter in result.parameters)
            or result.parameters_by_kind[
                signatures.Parameter.Kind.VARIADIC_POSITIONAL]
            or result.parameters_by_kind[
                signatures.Parameter.Kind.VARIADIC_KEYWORD])
