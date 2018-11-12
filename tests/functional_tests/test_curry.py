from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)
from typing import (Any,
                    Callable)

from paradigm.hints import (MethodDescriptorType,
                            WrapperDescriptorType)

from lz.functional import (Curry,
                           curry)


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

    if result.signature.has_unset_parameters():
        result_empty_call = result()

        assert isinstance(result_empty_call, Curry)
        assert are_curryings_equal(result_empty_call, result)


def are_curryings_equal(left_currying: Curry,
                        right_currying: Curry) -> bool:
    return (left_currying.func == right_currying.func
            and left_currying.args == right_currying.args
            and left_currying.keywords == right_currying.keywords
            and left_currying.signature == right_currying.signature)
