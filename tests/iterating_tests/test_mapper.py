from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.hints import Map
from lz.iterating import (first,
                          last,
                          mapper)
from tests.utils import is_empty


def test_base_case(map_: Map,
                   empty_iterable: Iterable[Any]) -> None:
    map_iterable = mapper(map_)

    result = map_iterable(empty_iterable)

    assert is_empty(result)


def test_step_left(map_: Map,
                   map_arguments: Iterable[Any],
                   map_argument: Any) -> None:
    map_iterable = mapper(map_)
    attach = left.attacher(map_argument)

    result = map_iterable(attach(map_arguments))

    assert first(result) == map_(map_argument)


def test_step_right(map_: Map,
                    map_arguments: Iterable[Any],
                    map_argument: Any) -> None:
    map_iterable = mapper(map_)
    attach = right.attacher(map_argument)

    result = map_iterable(attach(map_arguments))

    assert last(result) == map_(map_argument)
