from collections import abc
from typing import Sequence

from lz.functional import (cleave,
                           curry)
from lz.hints import (Domain,
                      Map)
from tests.utils import are_iterables_similar


def test_currying(maps: Sequence[Map],
                  map_argument: Domain) -> None:
    cleavage = cleave(*maps)
    curried_cleavage = curry(cleavage)

    result = curried_cleavage(map_argument)

    assert isinstance(result, abc.Iterable)
    assert are_iterables_similar(result, cleavage(map_argument))
