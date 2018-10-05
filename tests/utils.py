from itertools import (starmap,
                       zip_longest)
from operator import eq
from typing import (Any,
                    Iterable)

from hypothesis import (Phase,
                        core,
                        settings)
from hypothesis.errors import (NoSuchExample,
                               Unsatisfiable)
from hypothesis.searchstrategy import SearchStrategy


def find(strategy: SearchStrategy) -> Any:
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


def has_same_elements(left_iterable: Iterable[Any],
                      right_iterable: Iterable[Any]) -> bool:
    return all(starmap(eq, zip_longest(left_iterable, right_iterable,
                                       # we're assuming that ``object()``
                                       # will create some unique object
                                       # not presented in any of arguments
                                       fillvalue=object())))
