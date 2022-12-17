import functools as _functools
import itertools as _itertools
import typing as _t
from collections import (abc as _abc,
                         deque as _deque)

_T = _t.TypeVar('_T')


@_functools.singledispatch
def replicate(_value: _t.Any,
              *,
              count: int) -> _t.Iterable[_t.Any]:
    """
    Returns given number of object replicas.
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(_value)))


_Immutable = _t.TypeVar('_Immutable', bytes, object, str)


@replicate.register(object)
# immutable strings represent a special kind of iterables
# that can be replicated by simply repeating
@replicate.register(bytes)
@replicate.register(str)
def _(_value: _Immutable, *, count: int) -> _t.Iterable[_Immutable]:
    """
    Returns object repeated given number of times.
    """
    yield from _itertools.repeat(_value, count)


@replicate.register(_abc.Iterable)
def _replicate_iterable(_value: _t.Iterable[_T],
                        *,
                        count: int) -> _t.Iterable[_t.Iterable[_T]]:
    """
    Returns given number of iterable replicas.
    """
    iterator = iter(_value)
    queues: _t.Sequence[_t.Deque[_T]] = [
        _deque() for _ in _itertools.repeat(None, count)
    ]

    def replica(queue: _t.Deque[_T]) -> _t.Iterable[_T]:
        while True:
            if not queue:
                try:
                    element = next(iterator)
                except StopIteration:
                    return
                element_copies = replicate(element,
                                           count=count)
                for sub_queue, element_copy in zip(queues, element_copies):
                    sub_queue.append(element_copy)
            yield queue.popleft()

    yield from map(replica, queues)


@replicate.register(bytearray)
def _(_value: bytearray,
      *,
      count: int) -> _t.Iterable[bytearray]:
    for _ in _itertools.repeat(None, count):
        yield _value[:]


@replicate.register(frozenset)
def _(_value: _t.FrozenSet[_T],
      *,
      count: int) -> _t.Iterable[_t.FrozenSet[_T]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield frozenset(replica)


@replicate.register(list)
def _(_value: _t.List[_T],
      *,
      count: int) -> _t.Iterable[_t.List[_T]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield list(replica)


@replicate.register(set)
def _(_value: _t.Set[_T],
      *,
      count: int) -> _t.Iterable[_t.Set[_T]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield set(replica)


@replicate.register(tuple)
def _(_value: _t.Tuple[_T, ...],
      *,
      count: int) -> _t.Iterable[_t.Tuple[_T, ...]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield tuple(replica)


_Key = _t.TypeVar('_Key')
_Value = _t.TypeVar('_Value')


@replicate.register(dict)
def _(_value: _t.Dict[_Key, _Value],
      *,
      count: int) -> _t.Iterable[_t.Dict[_Key, _Value]]:
    for replica in _replicate_iterable(_value.items(),
                                       count=count):
        yield dict(replica)


def replicator(count: int) -> _t.Callable[[_T], _t.Iterable[_T]]:
    """
    Returns function that replicates passed object.

    >>> triplicate = replicator(3)
    >>> list(map(tuple, triplicate(range(5))))
    [(0, 1, 2, 3, 4), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4)]
    """
    return _functools.partial(replicate,
                              count=count)


duplicate = replicator(2)
duplicate.__doc__ = 'Duplicates given object.'
