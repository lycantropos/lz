from hypothesis import strategies

from tests.configs import MAX_ITERABLES_SIZE

non_negative_indices = strategies.integers(0, MAX_ITERABLES_SIZE - 1)
positive_indices = strategies.integers(1, MAX_ITERABLES_SIZE - 1)
