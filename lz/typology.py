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
    result = partial(is_instance_of,
                     types=types)
    result.__name__ = result.__qualname__ = (
            'is_instance_of_' + '_or_'.join(type_.__name__ for type_ in types))
    result.__doc__ = ('Checks if given object is instance '
                      'of one of types: "{types}".'
                      .format(types='", "'.join(type_.__qualname__
                                                for type_ in types)))
    return result


def subclass_of(*types: type) -> Predicate:
    """
    Creates predicate that checks if type is subclass of given types.

    >>> is_metaclass = subclass_of(type)
    >>> is_metaclass(type)
    True
    >>> is_metaclass(object)
    False
    """
    result = partial(is_subclass_of,
                     types=types)
    result.__name__ = result.__qualname__ = (
            'is_subclass_of_' + '_or_'.join(type_.__name__ for type_ in types))
    result.__doc__ = ('Checks if given type is subclass '
                      'of one of types: "{types}".'
                      .format(types='", "'.join(type_.__qualname__
                                                for type_ in types)))
    return result


def is_instance_of(object_: Any, types: Tuple[type, ...]) -> bool:
    return isinstance(object_, types)


def is_subclass_of(type_: type, types: Tuple[type, ...]) -> bool:
    return issubclass(type_, types)
