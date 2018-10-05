from hypothesis import strategies

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
deferred_objects = strategies.deferred(lambda: objects)
lists = strategies.lists(deferred_objects)
tuples = lists.map(tuple)
objects = (hashables
           | strategies.dictionaries(hashables, deferred_objects)
           | strategies.iterables(deferred_objects)
           | lists
           | strategies.sets(hashables)
           | tuples)
positionals_arguments = tuples
keywords_arguments = strategies.dictionaries(strings, objects)
