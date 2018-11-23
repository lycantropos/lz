from typing import (Any,
                    Dict,
                    Tuple)

from lz.functional import arguments_to_strings
from tests.utils import capacity


def test_capacity(positional_arguments: Tuple[Any, ...],
                  keyword_arguments: Dict[str, Any]) -> None:
    result = arguments_to_strings(positional_arguments, keyword_arguments)

    assert capacity(result) == (len(positional_arguments)
                                + len(keyword_arguments))


def test_elements(positional_arguments: Tuple[Any, ...],
                  keyword_arguments: Dict[str, Any]) -> None:
    result = arguments_to_strings(positional_arguments, keyword_arguments)

    assert all(isinstance(element, str)
               for element in result)
