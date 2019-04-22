from typing import (AnyStr,
                    Tuple)

from hypothesis import given

from lz.textual import rsplit
from tests.textual_tests import strategies


@given(strategies.any_strings_with_separators)
def test_keep_separator(any_string_with_separator: Tuple[AnyStr, AnyStr]
                        ) -> None:
    any_string, separator = any_string_with_separator
    parts = rsplit(any_string,
                   separator=separator,
                   keep_separator=True)

    empty_string = type(any_string)()

    assert empty_string.join(parts) == any_string


@given(strategies.any_strings_with_separators)
def test_skip_separator(any_string_with_separator: Tuple[AnyStr, AnyStr]
                        ) -> None:
    any_string, separator = any_string_with_separator
    parts = rsplit(any_string,
                   separator=separator,
                   keep_separator=False)

    assert separator.join(parts) == any_string
