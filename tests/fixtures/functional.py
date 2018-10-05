import pytest

from lz.hints import (Domain,
                      Intermediate,
                      Map,
                      Predicate,
                      Range)
from tests import strategies
from tests.utils import find


@pytest.fixture(scope='session')
def false_predicate() -> Predicate:
    return find(strategies.false_predicates)


@pytest.fixture(scope='session')
def predicate() -> Predicate:
    return find(strategies.predicates)


@pytest.fixture(scope='session')
def true_predicate() -> Predicate:
    return find(strategies.true_predicates)


@pytest.fixture(scope='session')
def map_() -> Map[Domain, Range]:
    return find(strategies.maps)


@pytest.fixture(scope='session')
def map_argument() -> Domain:
    return find(strategies.maps_arguments)


@pytest.fixture(scope='session')
def next_map(map_: Map[Domain, Range]) -> Map[Range, Intermediate]:
    return find(strategies.to_one_of_suitable_maps(map_))


@pytest.fixture(scope='session')
def last_map(next_map: Map[Range, Intermediate]) -> Map[Intermediate, Range]:
    return find(strategies.to_one_of_suitable_maps(next_map))
