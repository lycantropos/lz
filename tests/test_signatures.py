from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)

from lz import signatures
from lz.signatures.hints import MethodDescriptorType


def test_factory(function: FunctionType,
                 built_in_function: BuiltinFunctionType,
                 method: MethodType,
                 method_descriptor: MethodDescriptorType) -> None:
    built_in_function_result = signatures.factory(built_in_function)
    function_result = signatures.factory(function)
    method_result = signatures.factory(method)
    method_descriptor_result = signatures.factory(method_descriptor)

    assert isinstance(built_in_function_result, signatures.Base)
    assert isinstance(function_result, signatures.Base)
    assert isinstance(method_result, signatures.Base)
    assert isinstance(method_descriptor_result, signatures.Base)
