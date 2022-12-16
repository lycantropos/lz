from functools import partial
from typing import (Any,
                    Tuple)

from .hints import Predicate


def instance_of(*types: type) -> Predicate:
    """
    Creates predicate that checks if object is instance of given types.

    >>> is_any_string = instance_of(str, bytes, bytearray)
    >>> is_any_string(b'')
    True
    >>> is_any_string('')
    True
    >>> is_any_string(1)
    False
    """
    return partial(is_instance_of,
                   types=types)


def subclass_of(*types: type) -> Predicate:
    """
    Creates predicate that checks if type is subclass of given types.

    >>> is_metaclass = subclass_of(type)
    >>> is_metaclass(type)
    True
    >>> is_metaclass(object)
    False
    """
    return partial(is_subclass_of,
                   types=types)


def is_instance_of(value: Any, types: Tuple[type, ...]) -> bool:
    return isinstance(value, types)


def is_subclass_of(value: type, types: Tuple[type, ...]) -> bool:
    return issubclass(value, types)
