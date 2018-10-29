from typing import (Callable,
                    Dict,
                    Iterable,
                    List,
                    Tuple)

import pytest
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Intermediate,
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
def maps() -> List[Map]:
    return find(strategies.maps_lists)


@pytest.fixture(scope='function')
def maps_arguments() -> List[Domain]:
    return find(strategies.maps_lists_arguments)


@pytest.fixture(scope='function')
def next_map(map_: Map[Domain, Range]) -> Map[Range, Intermediate]:
    return find(strategies.to_one_of_suitable_maps(map_))


@pytest.fixture(scope='function')
def last_map(next_map: Map[Range, Intermediate]) -> Map[Intermediate, Range]:
    return find(strategies.to_one_of_suitable_maps(next_map))


@pytest.fixture(scope='function')
def suitable_maps() -> Tuple[Map, ...]:
    return find(strategies.suitable_maps)


@pytest.fixture(scope='function')
def next_suitable_map(suitable_maps: Tuple[Map, ...]) -> Map:
    return find(strategies.to_one_of_suitable_maps(suitable_maps[0]))


@pytest.fixture(scope='function')
def transparent_function() -> Callable[..., Range]:
    return find(strategies.transparent_functions)


@pytest.fixture(scope='function')
def transparent_function_args(transparent_function) -> Tuple[Domain, ...]:
    return find(strategies.to_transparent_functions_args(transparent_function))


@pytest.fixture(scope='function')
def transparent_function_kwargs(transparent_function) -> Dict[str, Domain]:
    return find(strategies
                .to_transparent_functions_kwargs(transparent_function))


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
    return find(strategies.to_iterables(projector_domain,
                                        min_size=1))
