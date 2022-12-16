from types import MethodType
from typing import (Tuple,
                    Type)

from hypothesis import given

from lz.functional import compose
from lz.hints import Domain
from tests.hints import CompositionCall
from . import strategies


@given(strategies.identifiers,
       strategies.empty.tuples,
       strategies.identifiers,
       strategies.two_maps_calls)
def test_method_definition(class_name: str,
                           class_bases: Tuple[Type, ...],
                           method_name: str,
                           maps_chain_call: CompositionCall) -> None:
    various_suitable_maps, map_argument = maps_chain_call
    composition = compose(*various_suitable_maps)
    method = compose(composition, ignore_self)
    class_ = type(class_name, class_bases, {method_name: method})
    instance = class_()

    bound_method = getattr(instance, method_name)

    assert isinstance(bound_method, MethodType)
    assert bound_method(map_argument) == composition(map_argument)


def ignore_self(self, argument: Domain) -> Domain:
    return argument
