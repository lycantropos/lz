from collections import abc
from typing import Sequence

from lz.functional import (combine,
                           curry)
from lz.hints import (Domain,
                      Map)
from tests.utils import are_iterables_similar


def test_currying(maps: Sequence[Map],
                  maps_arguments: Sequence[Domain]) -> None:
    combination = combine(*maps)
    curried_combination = curry(combination)

    result = curried_combination(maps_arguments)

    assert isinstance(result, abc.Iterable)
    assert are_iterables_similar(result, combination(maps_arguments))
