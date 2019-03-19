import sys
from functools import reduce
from itertools import repeat
from typing import (Any,
                    Callable,
                    Sequence,
                    Tuple)

from lz.functional import (compose,
                           identity)
from lz.hints import (Domain,
                      Map,
                      Range)
from tests.utils import (Intermediate,
                         implication,
                         not_raises)


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


def test_nesting(object_: Any) -> None:
    composition = reduce(compose,
                         repeat(identity,
                                times=sys.getrecursionlimit()),
                         identity)

    with not_raises(RecursionError):
        composition(object_)


def test_equality_base(suitable_maps: Sequence[Map],
                       other_suitable_maps: Sequence[Map],
                       map_argument: Domain) -> None:
    composition = compose(*suitable_maps)
    other_composition = compose(*other_suitable_maps)

    assert implication(composition == other_composition,
                       composition(map_argument)
                       == other_composition(map_argument))


def test_equality_reflexivity(suitable_maps: Sequence[Map]) -> None:
    composition = compose(*suitable_maps)

    assert composition == composition


def test_equality_symmetry(suitable_maps: Sequence[Map],
                           other_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*suitable_maps)
    other_composition = compose(*other_suitable_maps)

    assert implication(composition == other_composition,
                       other_composition == composition)


def test_equality_transitivity(suitable_maps: Sequence[Map],
                               other_suitable_maps: Sequence[Map],
                               another_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*suitable_maps)
    other_composition = compose(*other_suitable_maps)
    another_composition = compose(*another_suitable_maps)

    assert implication(composition == other_composition
                       and other_composition == another_composition,
                       other_composition == another_composition)
