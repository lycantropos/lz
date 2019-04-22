from functools import partial
from types import (BuiltinFunctionType,
                   FunctionType,
                   MethodType)

from hypothesis import given
from paradigm.hints import (MethodDescriptorType,
                            WrapperDescriptorType)

from lz.functional import (Curry,
                           curry)
from tests import strategies
from tests.utils import slow_data_generation


@slow_data_generation
@given(built_in_function=strategies.built_in_functions,
       class_=strategies.classes,
       function=strategies.functions,
       method=strategies.methods,
       method_descriptor=strategies.methods_descriptors,
       partial_callable=strategies.partial_callables,
       wrapper_descriptor=strategies.wrappers_descriptors)
def test_basic(built_in_function: BuiltinFunctionType,
               class_: type,
               function: FunctionType,
               method: MethodType,
               method_descriptor: MethodDescriptorType,
               partial_callable: partial,
               wrapper_descriptor: WrapperDescriptorType) -> None:
    for callable_ in (built_in_function,
                      class_,
                      function,
                      method,
                      method_descriptor,
                      partial_callable,
                      wrapper_descriptor):
        result = curry(callable_)

        assert isinstance(result, Curry)
