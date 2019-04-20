from typing import (Callable,
                    Iterable,
                    Sequence)

import pytest
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Range)
from tests import strategies
from tests.utils import find


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
