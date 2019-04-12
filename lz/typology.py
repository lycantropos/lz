from functools import partial
from operator import attrgetter
from typing import (Any,
                    Tuple)

from .hints import Predicate


def instance_of(*types: type) -> Predicate:
    """
    Creates predicate that checks if object is instance of given types.
    """
    predicate = partial(is_instance_of,
                        types=types)
    types_names = list(map(attrgetter('__name__'), types))
    predicate.__name__ = 'is_instance_of_' + '_or_'.join(types_names)
    predicate.__qualname__ = 'is_instance_of_' + '_or_'.join(types_names)
    types_full_names = map(attrgetter('__qualname__'), types)
    predicate.__doc__ = ('Checks if given object is instance '
                         'of one of types: "{types}".'
                         .format(types='", "'.join(types_full_names)))
    return predicate


def subclass_of(*types: type) -> Predicate:
    """
    Creates predicate that checks if type is subclass of given types.
    """
    predicate = partial(is_subclass_of,
                        types=types)
    types_names = list(map(attrgetter('__name__'), types))
    predicate.__name__ = 'is_subclass_of_' + '_or_'.join(types_names)
    predicate.__qualname__ = 'is_subclass_of_' + '_or_'.join(types_names)
    types_full_names = map(attrgetter('__qualname__'), types)
    predicate.__doc__ = ('Checks if given type is subclass '
                         'of one of types: "{types}".'
                         .format(types='", "'.join(types_full_names)))
    return predicate


def is_instance_of(object_: Any, types: Tuple[type, ...]) -> bool:
    return isinstance(object_, types)


def is_subclass_of(type_: type, types: Tuple[type, ...]) -> bool:
    return issubclass(type_, types)
