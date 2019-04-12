import copy
from typing import Sequence

from lz.functional import compose
from lz.hints import (Domain,
                      Map)


def test_shallow(various_suitable_maps: Sequence[Map],
                 map_argument: Domain) -> None:
    composition = compose(*various_suitable_maps)

    shallow_copy = copy.copy(composition)

    assert shallow_copy is not composition
    assert shallow_copy(map_argument) == composition(map_argument)


def test_deep(various_suitable_maps: Sequence[Map],
              map_argument: Domain) -> None:
    composition = compose(*various_suitable_maps)

    deep_copy = copy.deepcopy(composition)

    assert deep_copy is not composition
    assert deep_copy(map_argument) == composition(map_argument)
