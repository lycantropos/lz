from functools import partial
from typing import Optional

from hypothesis import strategies

from tests.hints import (RightFolderCall,
                         RightProjector,
                         Strategy)
from tests.strategies import (projectors,
                              to_homogeneous_sequences,
                              to_projectors_domains,
                              to_projectors_domains_initials)


def to_folder_calls(projector: RightProjector,
                    *,
                    min_size: int = 0,
                    max_size: Optional[int] = None) -> RightFolderCall:
    def from_domains(domains: Strategy[Strategy]) -> Strategy[RightFolderCall]:
        return strategies.tuples(strategies.just(projector),
                                 to_projectors_domains_initials((projector,
                                                                 domains)),
                                 to_homogeneous_sequences(domains,
                                                          min_size=min_size,
                                                          max_size=max_size))

    return to_projectors_domains(projector).flatmap(from_domains)


empty_folder_calls = projectors.flatmap(partial(to_folder_calls,
                                                max_size=0))
folder_calls = projectors.flatmap(to_folder_calls)
non_empty_folder_calls = projectors.flatmap(partial(to_folder_calls,
                                                    min_size=1))
