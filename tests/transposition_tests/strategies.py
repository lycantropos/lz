from functools import partial
from typing import (Any,
                    Iterable)

from hypothesis.searchstrategy import SearchStrategy as Strategy

from lz.hints import (Domain,
                      FiniteIterable)
from lz.transposition import transpose
from tests.strategies import (empty,
                              non_negative_indices,
                              objects,
                              positive_indices,
                              to_homogeneous_iterables,
                              to_tuples)

empty_iterables = empty.iterables


def to_transposable_iterables_elements(size: int,
                                       *,
                                       elements: Strategy[Domain] = objects
                                       ) -> Strategy[FiniteIterable[Domain]]:
    return to_tuples(elements,
                     size=size)


def to_transposable_iterables(size: int,
                              *,
                              elements: Strategy[Domain] = objects,
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


def is_untransposable_object(object_: Any) -> bool:
    return transpose.dispatch(type(object_)) is transpose.dispatch(object)


untransposable_objects = objects.filter(is_untransposable_object)
