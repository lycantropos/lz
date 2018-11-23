from typing import AnyStr

from lz.textual import split


def test_keep_separator(any_string: AnyStr,
                        any_separator: AnyStr) -> None:
    parts = split(any_string,
                  separator=any_separator,
                  keep_separator=True)

    empty_string = type(any_string)()

    assert empty_string.join(parts) == any_string


def test_skip_separator(any_string: AnyStr,
                        any_separator: AnyStr) -> None:
    parts = split(any_string,
                  separator=any_separator,
                  keep_separator=False)

    assert any_separator.join(parts) == any_string
