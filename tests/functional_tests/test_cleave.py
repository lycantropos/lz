from typing import List

from lz.functional import cleave
from lz.hints import (Domain,
                      Map)
from tests.utils import capacity


def test_capacity(maps: List[Map],
                  map_argument: Domain) -> None:
    cleft = cleave(maps)

    result = cleft(map_argument)

    assert capacity(result) == len(maps)


def test_elements(maps: List[Map],
                  map_argument: Domain) -> None:
    cleft = cleave(maps)

    result = cleft(map_argument)

    assert all(element == map_(map_argument)
               for element, map_ in zip(result, maps))
