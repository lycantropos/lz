import functools
from collections import (abc,
                         deque)
from typing import (Iterable,
                    Sequence)

from .hints import (Domain,
                    Range)


@functools.singledispatch
def transpose(object_: Domain) -> Range:
    """
    Transposes given object.
    """
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type))


@transpose.register(abc.Iterable)
def transpose_iterable(object_: Iterable[Iterable[Domain]]
                       ) -> Iterable[Iterable[Domain]]:
    """
    Transposes given iterable of finite iterables.
    """
    iterator = iter(object_)
    try:
        first_elements = next(iterator)
    except StopIteration:
        return
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

    yield from map(coordinate, queues)


@transpose.register(abc.Sequence)
def transpose_sequence(iterable: Sequence[Iterable[Domain]]
                       ) -> Iterable[Sequence[Domain]]:
    """
    Transposes given sequence of iterables.
    """
    yield from zip(*iterable)
