from hypothesis import strategies

strings = strategies.text()
scalars = (strategies.none()
           | strategies.booleans()
           | strategies.integers()
           | strategies.floats(allow_nan=True,
                               allow_infinity=True)
           | strategies.complex_numbers(allow_nan=True,
                                        allow_infinity=True)
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
