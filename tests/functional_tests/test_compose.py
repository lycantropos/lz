from typing import (Any,
                    Callable)

from lz.functional import (compose,
                           identity)
from lz.hints import (Domain,
                      Intermediate,
                      Map,
                      Range)


def test_self_composition(callable_: Callable[..., Any]) -> None:
    result = compose(callable_)

    assert result is callable_


def test_identity(map_: Map[Domain, Range],
                  map_argument: Domain) -> None:
    left_composition = compose(identity, map_)
    right_composition = compose(map_, identity)

    left_composition_result = left_composition(map_argument)
    right_composition_result = right_composition(map_argument)

    assert left_composition_result == right_composition_result


def test_associativity(last_map: Map[Intermediate, Range],
                       next_map: Map[Range, Intermediate],
                       map_: Map[Domain, Range],
                       map_argument: Domain) -> None:
    left_composition = compose(compose(last_map, next_map), map_)
    right_composition = compose(last_map, compose(next_map, map_))

    left_composition_result = left_composition(map_argument)
    right_composition_result = right_composition(map_argument)

    assert left_composition_result == right_composition_result
