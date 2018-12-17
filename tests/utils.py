import codecs
from collections import (abc,
                         defaultdict,
                         deque)
from functools import singledispatch
from itertools import (starmap,
                       zip_longest)
from operator import itemgetter
from typing import (Any,
                    Hashable,
                    Iterable,
                    Mapping,
                    Sized)

from hypothesis import (Phase,
                        core,
                        settings)
from hypothesis.errors import (NoSuchExample,
                               Unsatisfiable)
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import Domain


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
            if prefix_element != element:
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
    for key, value in object_.items():
        if not are_objects_similar(value, *map(itemgetter(key), rest)):
            return False
    return True


@are_objects_similar.register(abc.Iterable)
def are_iterables_similar(object_: Iterable[Any],
                          *rest: Iterable[Any]) -> bool:
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
