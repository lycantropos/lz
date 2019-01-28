from functools import partial
from numbers import Real
from operator import gt
from typing import (Any,
                    Dict,
                    Hashable,
                    Iterable,
                    Sequence,
                    Tuple)

import pytest
from hypothesis.searchstrategy import SearchStrategy as Strategy

from lz.functional import identity
from lz.hints import (FiniteIterable,
                      Sortable)
from lz.sorting import (Implementation,
                        Key,
                        with_key)
from tests import strategies
from tests.configs import MAX_MIN_ITERABLES_SIZE
from tests.utils import find


@pytest.fixture(scope='function')
def real_number() -> Real:
    return find(strategies.real_numbers)


@pytest.fixture(scope='function')
def non_zero_real_number() -> Real:
    def is_non_zero(number: Real) -> bool:
        return number != 0

    return find(strategies.real_numbers.filter(is_non_zero))


@pytest.fixture(scope='function')
def object_() -> Any:
    return find(strategies.objects)


@pytest.fixture(scope='function')
def positional_arguments() -> Tuple[Any, ...]:
    return find(strategies.positionals_arguments)


@pytest.fixture(scope='function')
def keyword_arguments() -> Dict[str, Any]:
    return find(strategies.keywords_arguments)


@pytest.fixture(scope='function')
def registered_sorting_algorithm() -> str:
    return find(strategies.registered_sorting_algorithms)


@pytest.fixture(scope='function')
def unregistered_sorting_algorithm() -> str:
    return find(strategies.unregistered_sorting_algorithms)


@pytest.fixture(scope='function')
def sorting_implementation() -> Implementation:
    return with_key(identity)


@pytest.fixture(scope='function')
def sorting_key() -> Key:
    return find(strategies.sorting_keys)


@pytest.fixture(scope='function')
def min_iterables_size() -> int:
    return find(strategies.iterables_sizes
                .filter(partial(gt, MAX_MIN_ITERABLES_SIZE)))


@pytest.fixture(scope='function')
def empty_iterable() -> Iterable[Any]:
    return find(strategies.empty.iterables)


@pytest.fixture(scope='function')
def empty_sequence() -> Iterable[Any]:
    return find(strategies.empty.sequences)


@pytest.fixture(scope='function')
def iterable(iterables_strategy: Strategy[Iterable[Any]]) -> Iterable[Any]:
    return find(iterables_strategy)


@pytest.fixture(scope='function')
def hashables_iterable(min_iterables_size: int) -> Iterable[Hashable]:
    return find(strategies.to_homogeneous_iterables(
            strategies.hashables,
            min_size=min_iterables_size))


@pytest.fixture(scope='function')
def sortable_iterable() -> Iterable[Sortable]:
    return find(strategies.sortable_iterables)


@pytest.fixture(scope='function')
def sequence(min_iterables_size: int) -> Iterable[Any]:
    limit_min_size = partial(partial,
                             min_size=min_iterables_size)
    return find(
            strategies.encodings.flatmap(limit_min_size(strategies
                                                        .to_byte_sequences))
            | limit_min_size(strategies
                             .to_homogeneous_sequences)(strategies.objects)
            | limit_min_size(strategies.to_strings)(strategies
                                                    .to_characters()))


@pytest.fixture(scope='function')
def non_empty_iterable() -> Iterable[Any]:
    limit_min_size = partial(partial,
                             min_size=1)
    return find(
            strategies.encodings.flatmap(limit_min_size(strategies
                                                        .to_any_streams))
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_byte_sequences))
            | limit_min_size(strategies
                             .to_homogeneous_iterables)(strategies.objects)
            | limit_min_size(strategies.to_strings)(strategies
                                                    .to_characters()))


@pytest.fixture(scope='function')
def non_empty_sequence() -> Sequence[Any]:
    limit_min_size = partial(partial,
                             min_size=1)
    return find(
            strategies.encodings.flatmap(limit_min_size(strategies
                                                        .to_byte_sequences))
            | limit_min_size(strategies
                             .to_homogeneous_sequences)(strategies.objects)
            | limit_min_size(strategies.to_strings)(strategies
                                                    .to_characters()))


@pytest.fixture(scope='function')
def nested_iterable(min_iterables_size: int,
                    iterables_strategy: Strategy[Iterable[Any]]
                    ) -> Iterable[Iterable[Any]]:
    limit_min_size = partial(partial,
                             min_size=min_iterables_size)
    return find(
            limit_min_size(strategies
                           .to_homogeneous_iterables)(iterables_strategy)
            | limit_min_size(strategies.to_strings)(strategies.to_characters())
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_text_streams)))


@pytest.fixture(scope='function')
def iterables_strategy(min_iterables_size: int) -> Strategy[Iterable[Any]]:
    limit_min_size = partial(partial,
                             min_size=min_iterables_size)
    return (strategies.encodings.flatmap(limit_min_size(strategies
                                                        .to_any_streams))
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_byte_sequences))
            | limit_min_size(strategies
                             .to_homogeneous_iterables)(strategies.objects)
            | limit_min_size(strategies.to_strings)(strategies
                                                    .to_characters()))


@pytest.fixture(scope='function')
def transposable_iterable(
        transposable_iterable_elements_strategy: Strategy[FiniteIterable[Any]]
) -> Iterable[FiniteIterable[Any]]:
    return find(strategies.to_homogeneous_iterables
                (transposable_iterable_elements_strategy))


@pytest.fixture(scope='function')
def non_empty_transposable_iterable(
        transposable_iterable_elements_strategy: Strategy[FiniteIterable[Any]],
        size: int) -> Iterable[FiniteIterable[Any]]:
    limit_min_size = partial(partial,
                             min_size=1)
    return find(limit_min_size(strategies.to_homogeneous_iterables)
                (strategies.to_tuples(strategies.objects,
                                      size=size + 1)))


@pytest.fixture(scope='function')
def transposable_iterable_element(
        transposable_iterable_elements_strategy: Strategy[FiniteIterable[Any]]
) -> FiniteIterable[Any]:
    return find(transposable_iterable_elements_strategy)


@pytest.fixture(scope='function')
def transposable_iterable_elements_strategy(size: int
                                            ) -> Strategy[FiniteIterable[Any]]:
    return strategies.to_tuples(strategies.objects,
                                size=size)
