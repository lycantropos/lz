import string

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from tests.configs import MAX_ITERABLES_SIZE
from .factories import (to_byte_sequences,
                        to_byte_strings,
                        to_characters,
                        to_dictionaries,
                        to_homogeneous_frozensets,
                        to_homogeneous_iterables,
                        to_homogeneous_lists,
                        to_homogeneous_sets,
                        to_homogeneous_tuples,
                        to_strings)

byte_strings = to_byte_strings()
strings = to_strings()
integers = (strategies.booleans()
            | strategies.integers())
real_numbers = (integers
                | strategies.floats(allow_nan=False,
                                    allow_infinity=False))
numbers = (real_numbers
           | strategies.complex_numbers(allow_nan=False,
                                        allow_infinity=False))
scalars = (strategies.none()
           | numbers
           | strategies.just(NotImplemented)
           | strategies.just(Ellipsis))
deferred_hashables = strategies.deferred(lambda: hashables)
hashables = (scalars
             | byte_strings
             | strings
             | to_homogeneous_frozensets(deferred_hashables)
             | to_homogeneous_tuples(deferred_hashables))
indices = strategies.integers(-MAX_ITERABLES_SIZE, MAX_ITERABLES_SIZE - 1)
slices_fields = strategies.none() | indices
slices = strategies.builds(slice,
                           slices_fields,
                           slices_fields,
                           slices_fields)
deferred_objects = strategies.deferred(lambda: objects)
iterables = (to_strings(to_characters())
             | to_byte_sequences()
             | to_homogeneous_iterables(deferred_objects))
sets = to_homogeneous_sets(hashables)
objects = (hashables
           | slices
           | iterables
           | sets
           | to_dictionaries(hashables, deferred_objects))
tuples = to_homogeneous_tuples(objects)
lists = to_homogeneous_lists(objects)


def extend_json(children: SearchStrategy) -> SearchStrategy:
    return (strategies.lists(children)
            | to_dictionaries(to_strings(string.printable),
                              children))


json_serializable_objects = strategies.recursive(
        strategies.none()
        | real_numbers
        | to_strings(string.printable),
        extend_json)
positionals_arguments = tuples
keywords_arguments = to_dictionaries(strings, objects)

sortable_domains = [real_numbers, sets, strings]
sortable_iterables = strategies.one_of(*map(to_homogeneous_iterables,
                                            sortable_domains))
