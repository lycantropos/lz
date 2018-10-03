from typing import (Callable,
                    TypeVar)

from typing_extensions import Protocol

Domain = TypeVar('Domain')
Intermediate = TypeVar('Intermediate')
Range = TypeVar('Range')
Map = Callable[[Domain], Range]
Operator = Map[Domain, Domain]
Predicate = Map[Domain, bool]


class Sortable(Protocol):
    def __lt__(self, other: 'Sortable') -> bool:
        pass
