import codecs
from collections import (abc,
                         defaultdict,
                         deque)
from functools import singledispatch
from itertools import (starmap,
                       zip_longest)
from operator import methodcaller
from typing import (Any,
                    Hashable,
                    Iterable,
                    Mapping,
                    Set,
                    Sized)

from hypothesis import (Phase,
                        core,
                        settings)
from hypothesis.errors import (NoSuchExample,
                               Unsatisfiable)
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import Domain
from lz.replication import duplicate


def find(strategy: SearchStrategy[Domain]) -> Domain:
    first_object_list = []

    def condition(object_: Any) -> bool:
        if first_object_list:
            return True
        else:
            first_object_list.append(object_)
            return False

    try:
        return core.find(strategy,
                         condition,
                         settings=settings(database=None,
                                           phases=tuple(set(Phase)
                                                        - {Phase.shrink})))
    except (NoSuchExample, Unsatisfiable) as search_error:
        try:
            result, = first_object_list
        except ValueError as unpacking_error:
            raise unpacking_error from search_error
        else:
            return result


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
    rest = tuple(map(dict, map(methodcaller('items'), rest)))
    for key, value in object_.items():
        rest_values = []
        for next_mapping in rest:
            try:
                next_value = next_mapping[key]
            except KeyError:
                if not isinstance(key, abc.Iterable):
                    raise
                candidates_keys = [key
                                   for key in next_mapping.keys()
                                   if isinstance(key, abc.Iterable)]
                for candidate_key in candidates_keys:
                    key, key_copy = duplicate(key)
                    candidate_value = next_mapping.pop(candidate_key)
                    (candidate_key,
                     candidate_key_copy) = duplicate(candidate_key)
                    if are_iterables_similar(key_copy, candidate_key_copy):
                        next_value = candidate_value
                        break
                    else:
                        next_mapping[candidate_key] = candidate_value
                else:
                    return False
            rest_values.append(next_value)
        if not are_objects_similar(value, *rest_values):
            return False
    return True


@are_objects_similar.register(abc.Set)
def are_sets_similar(object_: Set[Any], *rest: Set[Any]) -> bool:
    for next_set in rest:
        object_, object_copy = map(set, duplicate(object_))
        symmetric_difference = object_copy ^ next_set
        if not symmetric_difference:
            return True
        if not all(isinstance(element, abc.Iterable)
                   for element in symmetric_difference):
            return False
        while symmetric_difference:
            target = symmetric_difference.pop()
            candidates = iter(symmetric_difference)
            symmetric_difference = set()
            for candidate in candidates:
                target, target_copy = duplicate(target)
                candidate, candidate_copy = duplicate(candidate)
                if are_iterables_similar(target_copy, candidate_copy):
                    symmetric_difference.update(candidates)
                    break
                else:
                    symmetric_difference.add(candidate)
            else:
                return False
    return True


@are_objects_similar.register(abc.Iterable)
def are_iterables_similar(object_: Iterable[Any],
                          *rest: Iterable[Any]) -> bool:
    if any(not isinstance(candidate, abc.Iterable)
           for candidate in rest):
        return False
    return all(starmap(are_objects_similar,
                       zip_longest(object_, *rest,
                                   # we're assuming that ``object()``
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


@singledispatch
def capacity(iterable: Iterable[Any]) -> int:
    return sum(1 for _ in iterable)


@capacity.register(abc.Sized)
def sized_capacity(iterable: Sized) -> int:
    return len(iterable)


encoding_to_bom = (defaultdict(bytes,
                               {'utf_8_sig': codecs.BOM_UTF8,
                                'utf_16': codecs.BOM_UTF16,
                                'utf_16_be': codecs.BOM_UTF16_BE,
                                'utf_16_le': codecs.BOM_UTF16_LE,
                                'utf_32': codecs.BOM_UTF32,
                                'utf_32_be': codecs.BOM_UTF32_BE,
                                'utf_32_le': codecs.BOM_UTF32_LE})
                   .__getitem__)
