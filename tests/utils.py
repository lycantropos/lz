import codecs
from collections import defaultdict
from itertools import (starmap,
                       zip_longest)
from typing import (Any,
                    Iterable)

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


def are_iterables_similar(*iterables: Iterable[Any]) -> bool:
    return all(starmap(are_objects_equal,
                       zip_longest(*iterables,
                                   # we're assuming that ``object()``
                                   # will create some unique object
                                   # not presented in any of arguments
                                   fillvalue=object())))


def are_objects_equal(*objects: Iterable[Any]) -> bool:
    objects = iter(objects)
    previous_object = next(objects)
    for object_ in objects:
        if object_ != previous_object:
            return False
        previous_object = object_
    return True


def is_empty(iterable: Iterable[Any]) -> bool:
    try:
        next(iter(iterable))
    except StopIteration:
        return True
    else:
        return False


def capacity(iterable: Iterable[Any]) -> int:
    return sum(1 for _ in iterable)


encoding_to_bom = (defaultdict(bytes,
                               {'utf_8_sig': codecs.BOM_UTF8,
                                'utf_16': codecs.BOM_UTF16,
                                'utf_16_be': codecs.BOM_UTF16_BE,
                                'utf_16_le': codecs.BOM_UTF16_LE,
                                'utf_32': codecs.BOM_UTF32,
                                'utf_32_be': codecs.BOM_UTF32_BE,
                                'utf_32_le': codecs.BOM_UTF32_LE})
                   .__getitem__)
