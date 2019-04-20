from hypothesis import strategies

from tests.strategies import (iterables,
                              non_negative_indices,
                              positive_indices)

iterables = iterables
non_negative_slices_fields = strategies.none() | non_negative_indices
non_negative_slices = strategies.builds(slice,
                                        non_negative_slices_fields,
                                        non_negative_slices_fields,
                                        strategies.none() | positive_indices)
