from typing import (Any,
                    Dict,
                    Hashable,
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
def iterable() -> Iterable[Any]:
    return find(strategies.iterables)


@pytest.fixture(scope='function')
def hashables_iterable() -> Iterable[Hashable]:
    return find(strategies.hashables_iterables)
