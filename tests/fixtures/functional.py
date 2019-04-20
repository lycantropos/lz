from typing import (Callable,
                    Iterable,
                    Sequence)

import pytest
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Map,
                      Predicate,
                      Range)
from tests import strategies
from tests.utils import find


@pytest.fixture(scope='session')
def true_predicate() -> Predicate:
    return find(strategies.true_predicates)


@pytest.fixture(scope='session')
def false_predicate() -> Predicate:
    return find(strategies.false_predicates)


@pytest.fixture(scope='session')
def predicate() -> Predicate:
    return find(strategies.predicates)


@pytest.fixture(scope='session')
def left_predicate() -> Predicate:
    return find(strategies.predicates)


@pytest.fixture(scope='session')
def mid_predicate() -> Predicate:
    return find(strategies.predicates)


@pytest.fixture(scope='session')
def right_predicate() -> Predicate:
    return find(strategies.predicates)


@pytest.fixture(scope='session')
def predicate_argument() -> Domain:
    return find(strategies.predicates_arguments)


@pytest.fixture(scope='function')
def map_() -> Map:
    return find(strategies.maps)


@pytest.fixture(scope='function')
def map_argument() -> Domain:
    return find(strategies.maps_arguments)


@pytest.fixture(scope='function')
def map_arguments() -> Iterable[Domain]:
    return find(strategies.to_homogeneous_iterables(strategies.maps_arguments))


@pytest.fixture(scope='function')
def maps() -> Sequence[Map]:
    return find(strategies.maps_lists)


@pytest.fixture(scope='function')
def maps_arguments(maps: Sequence[Map]) -> Sequence[Domain]:
    maps_count = len(maps)
    return find(strategies.to_homogeneous_sequences(strategies.maps_arguments,
                                                    min_size=maps_count,
                                                    max_size=maps_count))


@pytest.fixture(scope='function')
def projector() -> Callable[[Domain, Domain], Domain]:
    return find(strategies.projectors)


@pytest.fixture(scope='function')
def projector_domain(projector: Callable[[Domain, Domain], Domain]
                     ) -> SearchStrategy:
    return find(strategies.to_projectors_domains(projector))


@pytest.fixture(scope='function')
def projector_domain_element(projector_domain: SearchStrategy) -> Domain:
    return find(projector_domain)


@pytest.fixture(scope='function')
def projector_initial(projector: Callable[[Domain, Domain], Domain],
                      projector_domain: SearchStrategy) -> Range:
    return find(strategies.to_projectors_domains_initials((projector,
                                                           projector_domain)))


@pytest.fixture(scope='function')
def projector_iterable(projector_domain: SearchStrategy) -> Iterable[Domain]:
    return find(strategies.to_homogeneous_iterables(projector_domain,
                                                    min_size=1))


@pytest.fixture(scope='function')
def projector_sequence(projector_domain: SearchStrategy) -> Sequence[Domain]:
    return find(strategies.to_homogeneous_sequences(projector_domain,
                                                    min_size=1))
