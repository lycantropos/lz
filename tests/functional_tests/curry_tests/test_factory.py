from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)

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
