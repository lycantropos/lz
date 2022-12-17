from typing import (Callable,
                    Iterable)

from hypothesis import given

from lz.iterating import (first,
                          last,
                          mapper)
from lz.replication import duplicate
from tests.hints import (Domain,
                         Range)
from tests.utils import is_empty
from . import strategies


@given(strategies.maps, strategies.empty_iterables)
def test_base_case(map_: Callable[[Domain], Range],
                   empty_iterable: Iterable[Domain]) -> None:
    map_iterable = mapper(map_)

    result = map_iterable(empty_iterable)

    assert is_empty(result)


@given(strategies.maps, strategies.non_empty_maps_arguments_iterables)
def test_step_left(map_: Callable[[Domain], Range],
                   arguments: Iterable[Domain]) -> None:
    original, target = duplicate(arguments)
    map_iterable = mapper(map_)

    result = map_iterable(target)

    assert first(result) == map_(first(original))


@given(strategies.maps, strategies.non_empty_maps_arguments_iterables)
def test_step_right(map_: Callable[[Domain], Range],
                    arguments: Iterable[Domain]) -> None:
    original, target = duplicate(arguments)
    map_iterable = mapper(map_)

    result = map_iterable(target)

    assert last(result) == map_(last(original))
