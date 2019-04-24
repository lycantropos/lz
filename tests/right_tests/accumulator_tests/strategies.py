from hypothesis import strategies

from tests.hints import (RightAccumulatorCall,
                         RightProjector,
                         Strategy)
from tests.strategies import (projectors,
                              to_homogeneous_sequences,
                              to_projectors_domains,
                              to_projectors_domains_initials)


def to_accumulator_calls(projector: RightProjector) -> RightAccumulatorCall:
    def from_domains(domains: Strategy[Strategy]
                     ) -> Strategy[RightAccumulatorCall]:
        return strategies.tuples(strategies.just(projector),
                                 to_projectors_domains_initials((projector,
                                                                 domains)),
                                 to_homogeneous_sequences(domains,
                                                          min_size=1))

    return to_projectors_domains(projector).flatmap(from_domains)


accumulator_calls = projectors.flatmap(to_accumulator_calls)
