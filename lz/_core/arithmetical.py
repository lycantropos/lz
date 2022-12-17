def ceil_division(dividend: int, divisor: int) -> int:
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
