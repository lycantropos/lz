import string

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from tests.configs import MAX_ITERABLES_SIZE
from .factories import (to_dictionaries,
                        to_frozensets,
                        to_iterables,
                        to_lists,
                        to_sets,
                        to_strings)

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
           | strings)
hashables = (scalars
             | to_frozensets(strategies.deferred(lambda: hashables))
             | to_lists(strategies.deferred(lambda: hashables))
             .map(tuple))
hashables_iterables = to_iterables(hashables)
deferred_objects = strategies.deferred(lambda: objects)
lists = to_lists(deferred_objects)
tuples = lists.map(tuple)
indices = strategies.integers(0, MAX_ITERABLES_SIZE)
slices_fields = strategies.none() | indices
slices = strategies.builds(slice,
                           slices_fields,
                           slices_fields,
                           slices_fields)
objects = (hashables
           | slices
           | to_dictionaries(hashables, deferred_objects)
           | to_iterables(deferred_objects)
           | lists
           | to_sets(hashables)
           | tuples)


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
