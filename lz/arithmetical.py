from numbers import Real
from typing import overload


@overload
def ceil_division(dividend: int, divisor: int) -> int:
    pass


@overload
def ceil_division(dividend: Real, divisor: Real) -> Real:
    pass


def ceil_division(dividend: Real, divisor: Real) -> Real:
    """
    Divides given numbers with ceiling.
    """
    return -(-dividend // divisor)
