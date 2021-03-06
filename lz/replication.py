import functools
import itertools
from collections import (abc,
                         deque)
from typing import (Iterable,
                    Tuple)

from .hints import (Domain,
                    Map)


@functools.singledispatch
def replicate(object_: Domain,
              *,
              count: int) -> Iterable[Domain]:
    """
    Returns given number of object replicas.
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@replicate.register(object)
# immutable strings represent a special kind of iterables
# that can be replicated by simply repeating
@replicate.register(bytes)
@replicate.register(str)
# mappings cannot be replicated as other iterables
# since they are iterable only by key
@replicate.register(abc.Mapping)
def _(object_: Domain,
      *,
      count: int) -> Iterable[Domain]:
    """
    Returns object repeated given number of times.
    """
    return itertools.repeat(object_, count)


@replicate.register(abc.Iterable)
def _replicate_iterable(object_: Iterable[Domain],
                        *,
                        count: int) -> Iterable[Iterable[Domain]]:
    """
    Returns given number of iterable replicas.
    """
    iterator = iter(object_)
    queues = [deque() for _ in itertools.repeat(None, count)]

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
def _(object_: Tuple[Domain, ...],
      *,
      count: int) -> Iterable[Tuple[Domain, ...]]:
    yield from map(tuple, _replicate_iterable(object_,
                                              count=count))


def replicator(count: int) -> Map[Domain, Iterable[Domain]]:
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
