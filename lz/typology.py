from functools import partial as _partial
import typing as _t


def instance_of(*types: type) -> _t.Callable[[_t.Any], bool]:
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
    non_types = [candidate
                 for candidate in types
                 if not isinstance(candidate, type)]
    if non_types:
        raise TypeError(non_types)
    return _partial(_is_instance_of,
                    types=types)


def subclass_of(*types: type) -> _t.Callable[[type], bool]:
    """
    Creates predicate that checks if type is subclass of given types.

    >>> is_metaclass = subclass_of(type)
    >>> is_metaclass(type)
    True
    >>> is_metaclass(object)
    False
    """
    non_types = [candidate
                 for candidate in types
                 if not isinstance(candidate, type)]
    if non_types:
        raise TypeError(non_types)
    return _partial(_is_subclass_of,
                    types=types)


def _is_instance_of(value: _t.Any, types: _t.Tuple[type, ...]) -> bool:
    return isinstance(value, types)


def _is_subclass_of(value: type, types: _t.Tuple[type, ...]) -> bool:
    return issubclass(value, types)
