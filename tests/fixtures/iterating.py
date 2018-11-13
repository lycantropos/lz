from typing import (Any,
                    Hashable)

import pytest

from lz.hints import Map
from tests import strategies
from tests.utils import find


@pytest.fixture(scope='function')
def grouper_key() -> Map[Any, Hashable]:
    return find(strategies.groupers_keys)


@pytest.fixture(scope='function')
def cutter_slice() -> slice:
    return find(strategies.cutter_slices)


@pytest.fixture(scope='function')
def chopper_size() -> int:
    return find(strategies.indices)


@pytest.fixture(scope='function')
def slider_size(min_iterables_size: int) -> int:
    return find(strategies.to_integers(0, min_iterables_size))
