from hypothesis import strategies

dictionaries = strategies.fixed_dictionaries({})
iterables = strategies.iterables(strategies.nothing())
lists = strategies.lists(strategies.nothing())
sets = strategies.sets(strategies.nothing())
strings = strategies.just('')
tuples = strategies.tuples()
