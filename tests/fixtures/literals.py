from typing import (Any,
                    Dict,
                    Iterable,
                    Tuple)

import pytest

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
def min_iterables_size() -> int:
    return find(strategies.to_integers(0, 100))


@pytest.fixture(scope='function')
def natural_number() -> int:
    return find(strategies.to_integers(0))


@pytest.fixture(scope='function')
def iterable(min_iterables_size: int) -> Iterable[Any]:
    return find(strategies.to_iterables(strategies.hashables,
                                        min_size=min_iterables_size))


@pytest.fixture(scope='function')
def empty_iterable() -> Iterable[Any]:
    return find(strategies.empty.iterables)


@pytest.fixture(scope='function')
def non_empty_iterable() -> Iterable[Any]:
    return find(strategies.to_iterables(strategies.hashables,
                                        min_size=1))


@pytest.fixture(scope='function')
def sortable_iterable() -> Iterable[Any]:
    return find(strategies.sortable_iterables)
