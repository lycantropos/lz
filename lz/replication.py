import functools
import itertools
from collections import (abc,
                         deque)
from typing import (Any,
                    Callable,
                    Deque,
                    Dict,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from .hints import Domain

_T = TypeVar('_T')


@functools.singledispatch
def replicate(_value: Any,
              *,
              count: int) -> Iterable[Any]:
    """
    Returns given number of object replicas.
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(_value)))


_Immutable = TypeVar('_Immutable', bytes, object, str)


@replicate.register(object)
# immutable strings represent a special kind of iterables
# that can be replicated by simply repeating
@replicate.register(bytes)
@replicate.register(str)
def _(_value: _Immutable, *, count: int) -> Iterable[_Immutable]:
    """
    Returns object repeated given number of times.
    """
    yield from itertools.repeat(_value, count)


@replicate.register(abc.Iterable)
def _replicate_iterable(_value: Iterable[_T],
                        *,
                        count: int) -> Iterable[Iterable[_T]]:
    """
    Returns given number of iterable replicas.
    """
    iterator = iter(_value)
    queues: Sequence[Deque[_T]] = [deque()
                                   for _ in itertools.repeat(None, count)]

    def replica(queue: deque) -> Iterable[Domain]:
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


@replicate.register(tuple)
def _(_value: Tuple[_T, ...],
      *,
      count: int) -> Iterable[Tuple[_T, ...]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield tuple(replica)


@replicate.register(list)
def _(_value: List[_T],
      *,
      count: int) -> Iterable[List[_T]]:
    for replica in _replicate_iterable(_value,
                                       count=count):
        yield list(replica)


_Key = TypeVar('_Key')
_Value = TypeVar('_Value')


@replicate.register(dict)
def _(_value: Dict[_Key, _Value],
      *,
      count: int) -> Iterable[Dict[_Key, _Value]]:
    result: Sequence[Dict[_Key, _Value]] = [
        {} for _ in itertools.repeat(None, count)
    ]
    for key, value in _value.items():
        for index, (key_replica, value_replica) in enumerate(
                zip(replicate(key,
                              count=count),
                    replicate(value,
                              count=count))
        ):
            result[index][key_replica] = value_replica
    yield from result


def replicator(count: int) -> Callable[[Domain], Iterable[Domain]]:
    """
    Returns function that replicates passed object.

    >>> triplicate = replicator(3)
    >>> list(map(tuple, triplicate(range(5))))
    [(0, 1, 2, 3, 4), (0, 1, 2, 3, 4), (0, 1, 2, 3, 4)]
    """
    return functools.partial(replicate,
                             count=count)


duplicate = replicator(2)
duplicate.__doc__ = 'Duplicates given object.'
