from functools import partial

from hypothesis import strategies

from tests.configs import MAX_ITERABLES_SIZE

to_integers = strategies.integers
limit_max_size = partial(partial,
                         max_size=MAX_ITERABLES_SIZE)
to_dictionaries = limit_max_size(strategies.dictionaries)
to_frozensets = limit_max_size(strategies.frozensets)
to_iterables = limit_max_size(strategies.iterables)
to_lists = limit_max_size(strategies.lists)
to_sets = limit_max_size(strategies.sets)
to_strings = limit_max_size(strategies.text)
