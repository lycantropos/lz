from numbers import Real
from typing import overload


@overload
def ceil_division(dividend: int, divisor: int) -> int:
    pass


def ceil_division(dividend: Real, divisor: Real) -> Real:
    """
    Divides given numbers with ceiling.

    >>> ceil_division(10, 2)
    5
    >>> ceil_division(10, -2)
    -5
    >>> ceil_division(10, 3)
    4
    >>> ceil_division(10, -3)
    -3
    >>> ceil_division(-10, -3)
    4
    >>> ceil_division(-10, 3)
    -3
    """
    return -(-dividend // divisor)
