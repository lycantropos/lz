from typing import (Callable,
                    Dict,
                    Tuple)

from lz.functional import pack
from lz.hints import (Domain,
                      Range)


def test_basic(transparent_function: Callable[..., Range],
               transparent_function_args: Tuple[Domain, ...],
               transparent_function_kwargs: Dict[str, Domain]) -> None:
    packed = pack(transparent_function)

    result = packed(transparent_function_args, transparent_function_kwargs)

    assert result == transparent_function(*transparent_function_args,
                                          **transparent_function_kwargs)
