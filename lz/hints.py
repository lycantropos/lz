from collections import abc
from typing import (Callable,
                    Container,
                    Iterable,
                    TypeVar)

from typing_extensions import Protocol

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Map = Callable[[Domain], Range]
Operator = Map[Domain, Domain]
Predicate = Map[Domain, bool]


class Sortable(Protocol):
    def __lt__(self, other: 'Sortable') -> bool:
        pass


try:
    from collections.abc import Collection
    from typing import Collection as FiniteIterable
except ImportError:
    # for Python 3.5
    class Collection(abc.Sized, abc.Iterable, abc.Container):
        __slots__ = ()

        @classmethod
        def __subclasshook__(cls, subclass: type) -> bool:
            if cls is Collection:
                mro = subclass.__mro__
                for method in ('__len__', '__iter__', '__contains__'):
                    for base_class in mro:
                        if method in base_class.__dict__:
                            if base_class.__dict__[method] is None:
                                return NotImplemented
                            break
                    else:
                        return NotImplemented
                return True
            return NotImplemented


    class FiniteIterable(abc.Sized, Iterable[Domain], Container[Domain],
                         extra=Collection):
        __slots__ = ()
