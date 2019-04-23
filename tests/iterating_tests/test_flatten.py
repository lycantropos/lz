from typing import (Any,
                    Iterable)

from hypothesis import given

from lz import (left,
                right)
from lz.iterating import flatten
from lz.replication import duplicate
from tests import strategies
from tests.utils import (is_empty,
                         iterable_ends_with,
                         iterable_starts_with,
                         slow_data_generation)


@given(strategies.empty.iterables)
def test_base_case(empty_iterable: Iterable[Any]) -> None:
    result = flatten(empty_iterable)

    assert is_empty(result)


@slow_data_generation
@given(strategies.nested_iterables, strategies.iterables)
def test_step_left(nested_iterable: Iterable[Iterable[Any]],
                   iterable: Iterable[Any]) -> None:
    original, target = duplicate(iterable)
    attach = left.attacher(target)

    result = flatten(attach(nested_iterable))

    assert iterable_starts_with(result, original)


@slow_data_generation
@given(strategies.nested_iterables, strategies.iterables)
def test_step_right(nested_iterable: Iterable[Iterable[Any]],
                    iterable: Iterable[Any]) -> None:
    original, target = duplicate(iterable)
    attach = right.attacher(target)

    result = flatten(attach(nested_iterable))

    assert iterable_ends_with(result, original)
