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
    for callable_ in (built_in_function,
                      class_,
                      function,
                      method,
                      method_descriptor,
                      wrapper_descriptor):
        result = curry(callable_)

        assert isinstance(result, Curry)


def test_call(callable_: Callable[..., Any]) -> None:
    curried_callable = curry(callable_)

    if curried_callable.signature.has_unset_parameters():
        curried_callable_empty_call = curried_callable()

        assert isinstance(curried_callable_empty_call, Curry)
        assert are_curryings_equal(curried_callable_empty_call,
                                   curried_callable)


def are_curryings_equal(left_currying: Curry,
                        right_currying: Curry) -> bool:
    return (left_currying.func == right_currying.func
            and left_currying.args == right_currying.args
            and left_currying.keywords == right_currying.keywords
            and left_currying.signature == right_currying.signature)
