import functools
import heapq
import itertools
from collections import ChainMap
from operator import itemgetter
from typing import (Callable,
                    Iterable,
                    Optional,
                    Sequence,
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


def with_key(plain: Operator[Iterable[Sortable]]) -> Implementation:
    def implementation(iterable: Iterable[Domain],
                       *,
                       key: Key = None) -> Iterable[Domain]:
        if key is None:
            yield from plain(iterable)
            return
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


@register_implementation('QUICKSORT')
@with_key
def quicksort(iterable: Iterable[Domain]) -> Iterable[Domain]:
    def sort_in_place(sequence: Sequence[Domain],
                      *,
                      start_index: int,
                      stop_index: int) -> None:
        if start_index >= stop_index:
            return
        pivot_index = partition(sequence,
                                start_index=start_index,
                                stop_index=stop_index)
        sort_in_place(sequence,
                      start_index=start_index,
                      stop_index=pivot_index - 1)
        sort_in_place(sequence,
                      start_index=pivot_index + 1,
                      stop_index=stop_index)

    def partition(sequence: Sequence[Domain],
                  *,
                  start_index: int,
                  stop_index: int) -> int:
        pivot_index = start_index
        start_element = sequence[start_index]
        for index in range(start_index + 1, stop_index + 1):
            if sequence[index] > start_element:
                continue
            pivot_index += 1
            sequence[index], sequence[pivot_index] = (sequence[pivot_index],
                                                      sequence[index])
        sequence[pivot_index], sequence[start_index] = (sequence[start_index],
                                                        sequence[pivot_index])
        return pivot_index

    result = list(iterable)
    sort_in_place(result,
                  start_index=0,
                  stop_index=len(result) - 1)
    return result


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
