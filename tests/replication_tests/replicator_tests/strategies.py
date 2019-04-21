from hypothesis import strategies

from tests.strategies import (iterables,
                              objects)

objects = objects
iterables = iterables
sizes = strategies.integers(0, 100)
