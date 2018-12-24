import functools
import heapq
import itertools
from operator import itemgetter
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

implementations = {}


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
                            implementation: Optional[Implementation] = None
                            ) -> Union[Operator[Implementation],
                                       Implementation]:
    if implementation is None:
        return functools.partial(register_implementation, algorithm)
    implementations[algorithm] = implementation
    return implementation


DEFAULT_ALGORITHM = 'TIMSORT'
register_implementation(DEFAULT_ALGORITHM, sorted)


def with_key(plain: Operator[Iterable[Sortable]]) -> Implementation:
    def implementation(iterable: Iterable[Domain],
                       *,
                       key: Key = None) -> Iterable[Domain]:
        if key is None:
            yield from plain(iterable)
        yield from map(itemgetter(2),
                       plain((key(element), index, element)
                             for index, element in enumerate(iterable)))

    return implementation


@register_implementation('HEAPSORT')
@with_key
def heapsort(iterable: Iterable[Domain]) -> Iterable[Domain]:
    heap = list(iterable)
    heapq.heapify(heap)
    for _ in itertools.repeat(None, len(heap)):
        yield heapq.heappop(heap)


def sorter(*,
           algorithm: str = DEFAULT_ALGORITHM,
           key: Map[Domain, Sortable] = None) -> Operator[Iterable[Domain]]:
    """
    Returns function that generates sorted iterable
    by given key with specified algorithm.
    """
    implementation = search_implementation(algorithm)

    def sort(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from implementation(iterable,
                                  key=key)

    return sort
