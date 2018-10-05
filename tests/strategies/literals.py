import string

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

strings = strategies.text()
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
             | strategies.frozensets(strategies.deferred(lambda: hashables))
             | strategies.lists(strategies.deferred(lambda: hashables))
             .map(tuple))
hashables_iterables = strategies.iterables(hashables)
deferred_objects = strategies.deferred(lambda: objects)
lists = strategies.lists(deferred_objects)
tuples = lists.map(tuple)
iterables = strategies.iterables(deferred_objects)
objects = (hashables
           | strategies.dictionaries(hashables, deferred_objects)
           | iterables
           | lists
           | strategies.sets(hashables)
           | tuples)


def extend_json(children: SearchStrategy) -> SearchStrategy:
    return (strategies.lists(children)
            | strategies.dictionaries(strategies.text(string.printable),
                                      children))


json_serializable_objects = strategies.recursive(
        strategies.none()
        | real_numbers
        | strategies.text(string.printable),
        extend_json)
positionals_arguments = tuples
keywords_arguments = strategies.dictionaries(strings, objects)
