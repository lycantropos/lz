from functools import partial
from typing import Iterable

from lz.hints import (Domain,
                      FiniteIterable)
from tests.hints import Strategy
from tests.strategies import (empty,
                              non_negative_indices,
                              positive_indices,
                              scalars,
                              to_homogeneous_iterables,
                              to_tuples)

empty_iterables = empty.iterables


def to_transposable_iterables_elements(size: int,
                                       *,
                                       elements: Strategy[Domain] = scalars
                                       ) -> Strategy[FiniteIterable[Domain]]:
    return to_tuples(elements,
                     size=size)


def to_transposable_iterables(size: int,
                              *,
                              elements: Strategy[Domain] = scalars,
                              min_size: int = 0
                              ) -> Strategy[Iterable[FiniteIterable[Domain]]]:
    return to_homogeneous_iterables(
            to_transposable_iterables_elements(size,
                                               elements=elements),
            min_size=min_size)


transposable_iterables = (non_negative_indices
                          .flatmap(to_transposable_iterables))
transposable_iterables_elements = (
    non_negative_indices.flatmap(to_transposable_iterables_elements))
non_empty_transposable_iterables = (
    positive_indices.flatmap(partial(to_transposable_iterables,
                                     min_size=1)))
