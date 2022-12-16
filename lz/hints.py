from typing import (Callable,
                    TypeVar)

from typing_extensions import Protocol

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Predicate = Callable[[Domain], bool]


class Sortable(Protocol):
    def __lt__(self, other: 'Sortable') -> bool:
        pass
