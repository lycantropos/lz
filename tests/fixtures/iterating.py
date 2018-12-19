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
def replicator_size() -> int:
    return find(strategies.to_integers(0, 100))


@pytest.fixture(scope='function')
def cutter_slice() -> slice:
    return find(strategies.non_negative_slices)


@pytest.fixture(scope='function')
def chopper_size() -> int:
    return find(strategies.to_integers(1))


@pytest.fixture(scope='function')
def slider_size() -> int:
    return find(strategies.to_integers(0))


@pytest.fixture(scope='function')
def positive_slider_size() -> int:
    return find(strategies.to_integers(1))
