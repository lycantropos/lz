from numbers import Real
from typing import overload


@overload
def ceil_division(left_number: int, right_number: int) -> int:
    pass


def ceil_division(left_number: Real, right_number: Real) -> Real:
    """
    Divides given numbers with ceiling.
    """
    return -(-left_number // right_number)
