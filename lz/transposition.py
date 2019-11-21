import functools
from collections import (abc,
                         deque)
from typing import (Iterable,
                    overload)

from .hints import (Collection,
                    Domain,
                    FiniteIterable,
                    Range)


@overload
def transpose(object_: Iterable[FiniteIterable[Domain]]
              ) -> FiniteIterable[Iterable[Domain]]:
    pass


@overload
def transpose(object_: FiniteIterable[Iterable[Domain]]
              ) -> Iterable[FiniteIterable[Domain]]:
    pass


@functools.singledispatch
def transpose(object_: Domain) -> Range:
    """
    Transposes given object.

    >>> list(map(tuple, transpose(zip(range(10), range(10, 20)))))
    [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)]
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type))


@transpose.register(abc.Iterable)
def _(object_: Iterable[FiniteIterable[Domain]]
      ) -> FiniteIterable[Iterable[Domain]]:
    """
    Transposes given iterable of finite iterables.
    """
    iterator = iter(object_)
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


@transpose.register(Collection)
def _(object_: FiniteIterable[Iterable[Domain]]
      ) -> Iterable[FiniteIterable[Domain]]:
    """
    Transposes given finite iterable of iterables.
    """
    yield from zip(*object_)
