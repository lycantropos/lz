from hypothesis import strategies

from .definitions import (built_in_functions,
                          callables,
                          classes,
                          functions,
                          methods,
                          methods_descriptors,
                          partial_callables,
                          wrappers_descriptors)
from .functional import (
    false_predicates,
    maps,
    maps_arguments,
    non_variadic_transparent_functions_calls_with_invalid_args,
    non_variadic_transparent_functions_calls_with_invalid_kwargs,
    partitioned_transparent_functions_calls,
    predicates,
    predicates_arguments,
    projectors,
    suitable_maps,
    to_one_of_suitable_maps,
    to_projectors_domains,
    to_projectors_domains_initials,
    transparent_functions,
    transparent_functions_calls,
    true_predicates,
    various_suitable_maps)
from .iterating import (non_negative_indices,
                        positive_indices)
from .literals import empty
from .literals.base import (any_strings,
                            booleans,
                            encodings,
                            hashables,
                            iterables,
                            keywords_arguments,
                            min_iterables_sizes,
                            objects,
                            pickleable_objects,
                            plain_hashables,
                            positionals_arguments,
                            real_numbers,
                            sortable_iterables)
from .literals.factories import (to_any_streams,
                                 to_any_strings,
                                 to_byte_sequences,
                                 to_byte_streams,
                                 to_homogeneous_iterables,
                                 to_homogeneous_sequences,
                                 to_separator,
                                 to_strings,
                                 to_text_streams,
                                 to_tuples)
from .sorting import (registered_sorting_algorithms,
                      sorting_keys,
                      unregistered_sorting_algorithms)
from .utils import identifiers

to_integers = strategies.integers
