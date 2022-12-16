import functools
from collections import (abc,
                         deque)
from typing import (Any,
                    Collection,
                    Iterable,
                    Iterator,
                    overload)

from .hints import Domain


@overload
def transpose(
        _value: Collection[Iterable[Domain]]
) -> Iterable[Collection[Domain]]:
    pass


@overload
def transpose(
        _value: Iterator[Collection[Domain]]
) -> Collection[Iterable[Domain]]:
    pass


def transpose(_value: Domain) -> Any:
    """
    Transposes given object.

    >>> list(map(tuple, transpose(zip(range(10), range(10, 20)))))
    [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)]
    """
    return _transpose(_value)


@functools.singledispatch
def _transpose(_value: Any) -> Any:
    raise TypeError(type(_value))


@_transpose.register(abc.Iterable)
def _(_value: Iterable[Collection[Domain]]) -> Collection[Iterable[Domain]]:
    iterator = iter(_value)
    try:
        first_elements = next(iterator)
    except StopIteration:
        return ()
    queues = [deque([element])
              for element in first_elements]

    def coordinate(queue: deque) -> Iterable[Domain]:
        while True:
            if not queue:
                try:
                    elements = next(iterator)
                except StopIteration:
                    return
                for sub_queue, element in zip(queues, elements):
                    sub_queue.append(element)
            yield queue.popleft()

    return tuple(map(coordinate, queues))


@_transpose.register(Collection)
def _(_value: Collection[Iterable[Domain]]) -> Iterable[Collection[Domain]]:
    yield from zip(*_value)
