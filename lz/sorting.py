import functools
from collections import ChainMap
from typing import (Callable,
                    Iterable,
                    Optional,
                    Union)

from .hints import (Domain,
                    Map,
                    Operator,
                    Sortable)

Key = Optional[Map[Domain, Sortable]]
Implementation = Callable[..., Iterable[Domain]]

stable_implementations = {}
unstable_implementations = {}
implementations = ChainMap(stable_implementations,
                           unstable_implementations)


def search_implementation(algorithm: str) -> Implementation:
    try:
        return implementations[algorithm]
    except KeyError as error:
        algorithms_str = ', '.join(map(repr, implementations))
        error_message = ('Algorithm is not found: {algorithm}. '
                         'Available algorithms are: {algorithms}.'
                         .format(algorithm=algorithm,
                                 algorithms=algorithms_str))
        raise LookupError(error_message) from error


def register_implementation(algorithm: str,
                            implementation: Optional[Implementation] = None,
                            *,
                            stable: bool = False
                            ) -> Union[Operator[Implementation],
                                       Implementation]:
    if implementation is None:
        return functools.partial(register_implementation, algorithm,
                                 stable=stable)
    if stable:
        stable_implementations[algorithm] = implementation
    else:
        unstable_implementations[algorithm] = implementation
    return implementation


DEFAULT_ALGORITHM = 'TIMSORT'
register_implementation(DEFAULT_ALGORITHM, sorted,
                        stable=True)


def sorter(*,
           algorithm: str = DEFAULT_ALGORITHM,
           key: Map[Domain, Sortable] = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that generates sorted iterable
    by given key with specified algorithm.
    """
    implementation = search_implementation(algorithm)
    return functools.partial(implementation,
                             key=key)
