from hypothesis import strategies

from tests.hints import (LeftAccumulatorCall,
                         LeftProjector,
                         Strategy)
from tests.strategies import (projectors,
                              to_homogeneous_iterables,
                              to_projectors_domains,
                              to_projectors_domains_initials)


def to_accumulator_calls(projector: LeftProjector) -> LeftAccumulatorCall:
    def from_domains(domains: Strategy[Strategy]
                     ) -> Strategy[LeftAccumulatorCall]:
        return strategies.tuples(strategies.just(projector),
                                 to_projectors_domains_initials((projector,
                                                                 domains)),
                                 to_homogeneous_iterables(domains,
                                                          min_size=1))

    return to_projectors_domains(projector).flatmap(from_domains)


accumulator_calls = projectors.flatmap(to_accumulator_calls)
