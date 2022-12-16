import codecs
import os
import pickle
from collections import (abc,
                         defaultdict,
                         deque)
from contextlib import contextmanager
from functools import singledispatch
from itertools import (chain,
                       starmap,
                       zip_longest)
from operator import methodcaller
from typing import (Any,
                    AnyStr,
                    Callable, Hashable,
                    IO,
                    Iterable,
                    Mapping,
                    Set,
                    Type)

import pytest

from lz.hints import (Domain,
                      Range)
from lz.replication import duplicate

try:
    from typing import ContextManager
except ImportError:
    from typing_extensions import ContextManager


def iterable_starts_with(iterable: Iterable[Any],
                         prefix: Iterable[Any]) -> bool:
    iterator = iter(iterable)
    for prefix_element in prefix:
        try:
            element = next(iterator)
        except StopIteration:
            return False
        else:
            if not are_objects_similar(prefix_element, element):
                return False
    return True


def iterable_ends_with(iterable: Iterable[Any],
                       suffix: Iterable[Any]) -> bool:
    suffix = list(suffix)
    end_elements = deque(iterable,
                         maxlen=len(suffix))
    return are_iterables_similar(end_elements, suffix)


def iterables_has_same_elements(left_iterable: Iterable[Any],
                                right_iterable: Iterable[Any]) -> bool:
    (left_iterable_first_copy,
     left_iterable_second_copy) = duplicate(left_iterable)
    (right_iterable_first_copy,
     right_iterable_second_copy) = duplicate(right_iterable)
    return (is_iterable_subset_of(left_iterable_first_copy,
                                  right_iterable_first_copy)
            and is_iterable_subset_of(right_iterable_second_copy,
                                      left_iterable_second_copy))


def is_iterable_subset_of(iterable: Iterable[Any],
                          target: Iterable[Any]) -> bool:
    for element in iterable:
        target, target_copy = duplicate(target)
        for target_element in target_copy:
            element, element_copy = duplicate(element)
            if are_objects_similar(element_copy, target_element):
                break
        else:
            return False
    return True


@singledispatch
def are_objects_similar(object_: Any, *rest: Any) -> bool:
    raise TypeError('Unsupported object type: {type}.'
                    .format(type=type(object_)))


@are_objects_similar.register(object)
@are_objects_similar.register(bytes)
@are_objects_similar.register(str)
def are_objects_equal(object_: Any, *rest: Any) -> bool:
    previous_object = object_
    for next_object in rest:
        if next_object != previous_object:
            return False
        previous_object = next_object
    return True


@are_objects_similar.register(abc.Mapping)
def are_mappings_similar(object_: Mapping[Hashable, Any],
                         *rest: Mapping[Hashable, Any]) -> bool:
    if not rest:
        return True
    if not all(isinstance(candidate, abc.Mapping)
               for candidate in rest):
        return False
    rest = tuple(map(dict, map(methodcaller('items'), rest)))
    for key, value in object_.items():
        for next_mapping in rest:
            try:
                next_value = next_mapping[key]
            except KeyError:
                if not isinstance(key, abc.Iterable):
                    return False
                candidates_keys = [key
                                   for key in next_mapping.keys()
                                   if isinstance(key, abc.Iterable)]
                for candidate_key in candidates_keys:
                    key, key_copy = duplicate(key)
                    value, value_copy = duplicate(value)
                    (candidate_value,
                     candidate_value_copy) = duplicate(next_mapping
                                                       .pop(candidate_key))
                    (candidate_key,
                     candidate_key_copy) = duplicate(candidate_key)
                    next_mapping[candidate_key] = candidate_value
                    if (are_objects_similar(key_copy,
                                            candidate_key_copy)
                            and are_objects_similar(value_copy,
                                                    candidate_value_copy)):
                        break
                else:
                    return False
            else:
                value, value_copy = duplicate(value)
                if not are_objects_similar(value, next_value):
                    return False
    return True


@are_objects_similar.register(abc.Set)
def are_sets_similar(object_: Set[Any], *rest: Set[Any]) -> bool:
    if not all(isinstance(next_set, abc.Set)
               for next_set in rest):
        return False
    for next_set in rest:
        object_, object_copy = map(set, duplicate(object_))
        symmetric_difference = set(object_copy ^ next_set)
        while symmetric_difference:
            target = symmetric_difference.pop()
            candidates = iter(symmetric_difference)
            symmetric_difference = set()
            for candidate in candidates:
                if not has_similar_types(candidate, target):
                    symmetric_difference.add(candidate)
                    continue
                target, target_copy = duplicate(target)
                candidate, candidate_copy = duplicate(candidate)
                if are_objects_similar(target_copy, candidate_copy):
                    symmetric_difference.update(candidates)
                    break
                else:
                    symmetric_difference.add(candidate)
            else:
                return False
    return True


def has_similar_types(left_object: Any, right_object: Any) -> bool:
    if isinstance(left_object, abc.Iterator):
        return isinstance(right_object, abc.Iterator)
    left_type = type(left_object)
    right_type = type(right_object)
    return (issubclass(left_type, right_type)
            or issubclass(right_type, left_type))


@are_objects_similar.register(abc.Iterable)
def are_iterables_similar(object_: Iterable[Any],
                          *rest: Iterable[Any]) -> bool:
    if any(not isinstance(candidate, abc.Iterable)
           for candidate in rest):
        return False
    return all(starmap(are_objects_similar,
                       zip_longest(object_, *rest,
                                   # we're assuming that `object()`
                                   # will create some unique object
                                   # not presented in any of arguments
                                   fillvalue=object())))


def is_empty(iterable: Iterable[Any]) -> bool:
    try:
        next(iter(iterable))
    except StopIteration:
        return True
    else:
        return False


encoding_to_bom = (defaultdict(bytes,
                               {'utf_8_sig': codecs.BOM_UTF8,
                                'utf_16': codecs.BOM_UTF16,
                                'utf_16_be': codecs.BOM_UTF16_BE,
                                'utf_16_le': codecs.BOM_UTF16_LE,
                                'utf_32': codecs.BOM_UTF32,
                                'utf_32_be': codecs.BOM_UTF32_BE,
                                'utf_32_le': codecs.BOM_UTF32_LE})
                   .__getitem__)


def flatmap(function: Callable[[Domain], Iterable[Range]],
            *iterables: Iterable[Domain]) -> Iterable[Range]:
    yield from chain.from_iterable(map(function, *iterables))


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return not left_statement ^ right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


@contextmanager
def not_raises(*exceptions_classes: Type[Exception]) -> ContextManager[None]:
    try:
        yield
    except exceptions_classes as error:
        raise pytest.fail('RAISED {}'.format(type(error)))


def round_trip_pickle(object_: Any) -> Any:
    return pickle.loads(pickle.dumps(object_))


def is_pickleable(object_: Any) -> bool:
    try:
        pickle.dumps(object_)
    except pickle.PicklingError:
        return False
    else:
        return True


def to_stream_contents(stream: IO[AnyStr]) -> AnyStr:
    result = stream.read()
    stream.seek(0)
    return result


def to_stream_size(stream: IO[AnyStr]) -> int:
    result = stream.seek(0, os.SEEK_END)
    stream.seek(0)
    return result
