import itertools
from typing import (Callable,
                    Iterable)

from . import left
from .functional import (arguments_to_strings,
                         compose,
                         flip,
                         handle_partial,
                         update_metadata)
from .hints import (Domain,
                    Map,
                    Range)
from .iterating import (expand,
                        reverse)


def accumulator(function: Callable[[Domain, Range], Range],
                initial: Range
                ) -> Map[Iterable[Domain], Iterable[Iterable[Range]]]:
    """
    Returns function that yields cumulative results of given binary function
    starting from given initial object in direction from right to left.
    """
    left_accumulator = left.accumulator(flip(function), initial)
    return compose(left_accumulator, reverse)


def attacher(object_: Domain) -> Map[Iterable[Domain], Iterable[Domain]]:
    """
    Returns function that appends given object to iterable.
    """

    def attach(iterable: Iterable[Domain]) -> Iterable[Domain]:
        yield from itertools.chain(iterable, expand(object_))

    return attach


def folder(function: Callable[[Domain, Range], Range],
           initial: Range) -> Map[Iterable[Domain], Range]:
    """
    Returns function that cumulatively applies given binary function
    starting from given initial object in direction from right to left.
    """
    left_folder = left.folder(flip(function), initial)
    return compose(left_folder, reverse)


@handle_partial
def applier(function: Callable[..., Range],
            *args: Domain,
            **kwargs: Domain) -> Callable[..., Range]:
    """
    Returns function that behaves like given function
    with given arguments partially applied.
    Positional arguments will be applied from the right end.
    """

    def applied(*rest_args, **rest_kwargs) -> Range:
        return function(*rest_args, *applied.args,
                        **applied.keywords, **rest_kwargs)

    applied.func = function
    applied.args = args[::-1]
    applied.keywords = kwargs

    def name_factory(original: str) -> str:
        result = original
        arguments_strings = list(arguments_to_strings(applied.args,
                                                      applied.keywords))
        if arguments_strings:
            result += (' with right partially applied {arguments}'
                       .format(arguments=', '.join(arguments_strings)))
        return result

    update_metadata(function, applied,
                    name_factory=name_factory)
    return applied