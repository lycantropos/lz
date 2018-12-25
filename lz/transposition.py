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
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type))


@transpose.register(abc.Iterable)
def transpose_finite_iterables(object_: Iterable[FiniteIterable[Domain]]
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
def transpose_finite_iterable(object_: FiniteIterable[Iterable[Domain]]
                              ) -> Iterable[FiniteIterable[Domain]]:
    """
    Transposes given finite iterable of iterables.
    """
    yield from zip(*object_)
