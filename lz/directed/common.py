from collections import OrderedDict
from functools import partial
from itertools import (chain,
                       count)
from operator import (is_not,
                      itemgetter)
from typing import (Iterable,
                    Tuple)

from lz.functional import compose
from lz.hints import (Domain,
                      Map,
                      Operator)
from lz.iterating import (enumerator,
                          mapper,
                          separator,
                          sorter)
from lz.literal import to_unique_object

gap = to_unique_object()


def to_applier_flow(applied_args: Iterable[Domain],
                    *,
                    start: int,
                    step: int,
                    rest_start_factory: Map[Iterable[int], int]
                    ) -> Operator[Iterable[Domain]]:
    to_argument_index = itemgetter(0)
    to_argument_value = itemgetter(1)
    split_args = compose(separator(compose(partial(is_not, gap),
                                           itemgetter(1))),
                         enumerator(start=start,
                                    step=step))
    placeholders, occupied_args = split_args(applied_args)
    placeholders = OrderedDict(placeholders)
    occupied_args = list(occupied_args)
    occupied_indices = map(to_argument_index, occupied_args)

    def enumerate_rest(args: Iterable[Domain]) -> Iterable[Tuple[int, Domain]]:
        open_indices = chain(placeholders.keys(),
                             count(rest_start_factory(occupied_indices), step))
        yield from zip(open_indices, args)

    return compose(mapper(to_argument_value),
                   sorter(to_argument_index),
                   partial(chain, occupied_args),
                   enumerate_rest)
