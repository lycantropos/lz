from typing import List

from lz.functional import combine
from lz.hints import (Domain,
                      Map)
from tests.utils import capacity


def test_capacity(maps: List[Map],
                  maps_arguments: List[Domain]) -> None:
    combined = combine(maps)

    result = combined(maps_arguments)

    assert capacity(result) == min(len(maps), len(maps_arguments))


def test_elements(maps: List[Map],
                  maps_arguments: List[Domain]) -> None:
    combined = combine(maps)

    result = combined(maps_arguments)

    assert all(element == map_(map_argument)
               for element, map_, map_argument in zip(result,
                                                      maps, maps_arguments))
