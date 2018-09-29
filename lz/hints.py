from typing import (Any,
                    Callable,
                    Dict,
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


Namespace = Dict[str, Any]

try:
    from types import MethodDescriptorType
except ImportError:
    MethodDescriptorType = type(list.append)
