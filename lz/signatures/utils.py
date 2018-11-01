from functools import wraps
from typing import (Any,
                    MutableMapping)

from lz.hints import (Domain,
                      Map,
                      Operator,
                      Range)


def cached_map(cache: MutableMapping[Any, Any],
               *,
               update: bool = False) -> Operator[Map[Domain, Range]]:
    def wrapper(map_: Map[Domain, Range]) -> Map[Domain, Range]:
        @wraps(map_)
        def wrapped(argument: Domain) -> Range:
            try:
                return cache[argument]
            except KeyError:
                result = map_(argument)
                if update:
                    cache[argument] = result
                return result

        return wrapped

    return wrapper
