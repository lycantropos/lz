from typing import Sequence

from lz.functional import compose
from lz.hints import (Domain,
                      Map)
from tests.utils import implication


def test_base(various_suitable_maps: Sequence[Map],
              other_various_suitable_maps: Sequence[Map],
              map_argument: Domain) -> None:
    composition = compose(*various_suitable_maps)
    other_composition = compose(*other_various_suitable_maps)

    assert implication(composition == other_composition,
                       composition(map_argument)
                       == other_composition(map_argument))


def test_reflexivity(various_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*various_suitable_maps)

    assert composition == composition


def test_symmetry(various_suitable_maps: Sequence[Map],
                  other_various_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*various_suitable_maps)
    other_composition = compose(*other_various_suitable_maps)

    assert implication(composition == other_composition,
                       other_composition == composition)


def test_transitivity(various_suitable_maps: Sequence[Map],
                      other_various_suitable_maps: Sequence[Map],
                      another_various_suitable_maps: Sequence[Map]) -> None:
    composition = compose(*various_suitable_maps)
    other_composition = compose(*other_various_suitable_maps)
    another_composition = compose(*another_various_suitable_maps)

    assert implication(composition == other_composition
                       and other_composition == another_composition,
                       other_composition == another_composition)
