import json
import os
import string
from collections import OrderedDict
from decimal import Decimal
from operator import (add,
                      and_,
                      or_,
                      sub,
                      xor)
from typing import (Any,
                    Tuple)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.functional import (identity,
                           to_constant)
from lz.hints import (Map,
                      Predicate)
from .literals import empty
from .literals.base import (classes,
                            integers,
                            json_serializable_objects,
                            lists,
                            numbers,
                            objects,
                            real_numbers,
                            sets,
                            sortable_domains,
                            strings,
                            tuples)
from .literals.factories import (to_homogeneous_lists,
                                 to_strings)

false_predicates = strategies.just(to_constant(False))
true_predicates = strategies.just(to_constant(True))


def to_is_instance_predicate(class_: type) -> Predicate:
    def predicate(object_: Any) -> bool:
        return isinstance(object_, class_)

    predicate.__name__ = 'is_instance_of' + class_.__name__
    predicate.__qualname__ = 'is_instance_of' + class_.__qualname__
    return predicate


is_instance_predicates = classes.map(to_is_instance_predicate)
predicates = false_predicates | true_predicates | is_instance_predicates
predicates_arguments = objects
starting_maps = [identity, float, str, json.dumps]
suitable_maps = {identity: [identity, float, str],
                 float: starting_maps,
                 str: [identity, float, str, json.loads],
                 json.dumps: [identity, float, str, json.loads],
                 json.loads: starting_maps}
suitable_maps = dict(zip(suitable_maps.keys(),
                         map(strategies.sampled_from, suitable_maps.values())))
to_one_of_suitable_maps = suitable_maps.__getitem__
maps = strategies.sampled_from(starting_maps)
maps_lists = to_homogeneous_lists(maps)
maps_arguments = (strategies.integers()
                  | strategies.floats(allow_nan=False,
                                      allow_infinity=False))
maps_lists_arguments = to_homogeneous_lists(maps_arguments)


@strategies.composite
def extend_suitable_maps(draw: Map[SearchStrategy, Any],
                         maps_tuples: SearchStrategy) -> Tuple[Map, ...]:
    maps_tuple = draw(maps_tuples)
    last_map = draw(to_one_of_suitable_maps(maps_tuple[0]))
    return (last_map,) + maps_tuple


suitable_maps = strategies.recursive(strategies.tuples(maps),
                                     extend_suitable_maps)
# "transparent" is an abbr. of "referential transparent"
transparent_functions = strategies.sampled_from([bool, complex, float,
                                                 identity, int,
                                                 json.dumps, json.loads,
                                                 os.path.join, str])
paths_names_parts = to_strings(string.digits + string.ascii_letters + '_')
transparent_functions_args = {
    bool: strategies.tuples(objects),
    complex: strategies.tuples(numbers),
    float: strategies.tuples(real_numbers),
    identity: strategies.tuples(objects),
    int: strategies.tuples(integers),
    json.dumps: strategies.tuples(json_serializable_objects),
    json.loads: strategies.tuples(json_serializable_objects.map(json.dumps)),
    os.path.join: to_homogeneous_lists(paths_names_parts,
                                       min_size=1).map(tuple),
    str: strategies.tuples(objects),
}
transparent_functions_kwargs = {
    bool: empty.dictionaries,
    complex: empty.dictionaries,
    float: empty.dictionaries,
    identity: empty.dictionaries,
    int: empty.dictionaries,
    json.dumps: strategies.fixed_dictionaries(
            {'indent': strategies.integers(0, 10),
             'sort_keys': strategies.booleans()}),
    json.loads: strategies.fixed_dictionaries({
        'object_pairs_hook': strategies.none() | strategies.just(OrderedDict),
        'parse_float': strategies.none() | strategies.sampled_from([float,
                                                                    Decimal]),
        'parse_int': strategies.none() | strategies.sampled_from([int,
                                                                  float])}),
    os.path.join: empty.dictionaries,
    str: empty.dictionaries,
}
to_transparent_functions_args = transparent_functions_args.__getitem__
to_transparent_functions_kwargs = transparent_functions_kwargs.__getitem__
projectors = strategies.sampled_from([add, and_, max, min, or_,
                                      os.path.join, sub, xor])
projectors_domains = {add: [lists, numbers, strings, tuples],
                      and_: [sets],
                      max: sortable_domains,
                      min: sortable_domains,
                      or_: [sets],
                      os.path.join: [paths_names_parts],
                      sub: [numbers, sets],
                      xor: [sets]}
projectors_domains = dict(zip(projectors_domains.keys(),
                              map(strategies.sampled_from,
                                  projectors_domains.values())))
projectors_domains_initials = {
    (add, lists): empty.lists,
    (add, numbers): strategies.just(0),
    (and_, sets): sets,
    (add, strings): empty.strings,
    (add, tuples): empty.tuples,
    (max, real_numbers): strategies.just(float('-inf')),
    (max, sets): empty.sets,
    (max, strings): empty.strings,
    (min, real_numbers): strategies.just(float('inf')),
    (min, sets): empty.sets,
    (min, strings): empty.strings,
    (or_, sets): empty.sets,
    (os.path.join, paths_names_parts): empty.strings,
    (sub, numbers): strategies.just(0),
    (sub, sets): empty.sets,
    (xor, sets): empty.sets
}
to_projectors_domains = projectors_domains.__getitem__
to_projectors_domains_initials = projectors_domains_initials.__getitem__
