from numbers import Real


def ceil_division(left_number: Real, right_number: Real) -> Real:
    """
    Divides given numbers with ceiling.
    """
    return -(-left_number // right_number)
