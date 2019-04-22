from hypothesis import strategies

from tests.strategies import (iterables,
                              scalars)

scalars = scalars
iterables = iterables
sizes = strategies.integers(0, 100)
