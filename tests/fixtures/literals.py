from functools import partial
from typing import (Any,
                    Dict,
                    Hashable,
                    Iterable,
                    Sequence,
                    Tuple)

import pytest
from hypothesis.searchstrategy import SearchStrategy as Strategy

from lz.functional import identity
from lz.hints import Sortable
from lz.reversal import reverse
from lz.sorting import (Implementation,
                        Key,
                        with_key)
from tests import strategies
from tests.utils import find


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
    return find(strategies.min_iterables_sizes)


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
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_strings)))


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
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_strings)))


@pytest.fixture(scope='function')
def nested_iterable(min_iterables_size: int,
                    iterables_strategy: Strategy[Iterable[Any]]
                    ) -> Iterable[Iterable[Any]]:
    limit_min_size = partial(partial,
                             min_size=min_iterables_size)
    return find(
            limit_min_size(strategies
                           .to_homogeneous_iterables)(iterables_strategy)
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_strings))
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
            | strategies.encodings.flatmap(limit_min_size(strategies
                                                          .to_strings)))


@pytest.fixture(scope='function')
def irreversible_object() -> Any:
    def is_object_irreversible(object_: Any) -> bool:
        return reverse.dispatch(type(object_)) is reverse.dispatch(object)

    return find(strategies.objects.filter(is_object_irreversible))
