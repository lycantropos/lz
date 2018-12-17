from numbers import Real

from lz.arithmetical import ceil_division


def test_basic(real_number: Real,
               non_zero_real_number: Real) -> None:
    result = ceil_division(real_number, non_zero_real_number)

    quotient = real_number // non_zero_real_number

    if isinstance(real_number, int) and isinstance(non_zero_real_number, int):
        assert quotient <= result <= quotient + 1
    else:
        assert quotient <= result <= quotient + 2
