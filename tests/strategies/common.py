from hypothesis import strategies

scalars = (strategies.none()
           | strategies.booleans()
           | strategies.integers()
           | strategies.floats(allow_nan=True,
                               allow_infinity=True)
           | strategies.text())
hashables = (scalars
             | strategies.frozensets(strategies.deferred(lambda: hashables))
             | strategies.lists(strategies.deferred(lambda: hashables))
             .map(tuple))
dictionaries = strategies.dictionaries(hashables,
                                       strategies.deferred(lambda: objects))
iterables = strategies.iterables(strategies.deferred(lambda: objects))
lists = strategies.lists(strategies.deferred(lambda: objects))
sets = strategies.sets(hashables)
tuples = lists.map(tuple)
objects = (dictionaries
           | hashables
           | iterables
           | lists
           | sets
           | tuples)
