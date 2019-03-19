from typing import (Any,
                    Callable,
                    Tuple)

from lz.functional import compose
from lz.hints import (Domain,
                      Map,
                      Range)
from tests.utils import Intermediate


def test_base_case(callable_: Callable[..., Any]) -> None:
    composition = compose(callable_)

    assert composition is callable_


def test_step(suitable_maps: Tuple[Map[Domain, Intermediate], ...],
              next_suitable_map: Map[Intermediate, Range],
              map_argument: Domain) -> None:
    composition = compose(*suitable_maps)
    next_composition = compose(next_suitable_map, *suitable_maps)

    result = composition(map_argument)
    next_result = next_composition(map_argument)

    assert next_result == next_suitable_map(result)
