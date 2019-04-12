from typing import (Any,
                    Callable,
                    Dict)

from lz.functional import (curry,
                           pack)
from lz.hints import Domain


def test_currying(transparent_function: Callable[..., Any],
                  transparent_function_args: Domain,
                  transparent_function_kwargs: Dict[str, Domain]) -> None:
    packed = pack(transparent_function)
    curried_packed = curry(packed)

    result = curried_packed(transparent_function_args,
                            transparent_function_kwargs)

    assert result == packed(transparent_function_args,
                            transparent_function_kwargs)
