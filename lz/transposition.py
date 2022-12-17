import functools
from collections import (abc,
                         deque)
import typing as _t

_T = _t.TypeVar('_T')


@_t.overload
def transpose(
        _value: _t.Collection[_t.Iterable[_T]]
) -> _t.Iterable[_t.Collection[_T]]:
    pass


@_t.overload
def transpose(
        _value: _t.Iterator[_t.Collection[_T]]
) -> _t.Collection[_t.Iterable[_T]]:
    pass


def transpose(_value: _T) -> _t.Any:
    """
    Transposes given object.

    >>> list(map(tuple, transpose(zip(range(10), range(10, 20)))))
    [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)]
    """
    return _transpose(_value)


@functools.singledispatch
def _transpose(_value: _t.Any) -> _t.Any:
    raise TypeError(type(_value))


@_transpose.register(abc.Iterable)
def _(
        _value: _t.Iterable[_t.Collection[_T]]
) -> _t.Collection[_t.Iterable[_T]]:
    iterator = iter(_value)
    try:
        first_elements = next(iterator)
    except StopIteration:
        return ()
    queues = [deque([element]) for element in first_elements]

    def coordinate(queue: deque) -> _t.Iterable[_T]:
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


@_transpose.register(abc.Collection)
def _(
        _value: _t.Collection[_t.Iterable[_T]]
) -> _t.Iterable[_t.Collection[_T]]:
    yield from zip(*_value)
