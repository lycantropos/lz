import json
import os
import string
from collections import OrderedDict
from decimal import Decimal

from hypothesis import strategies

from lz.functional import (identity,
                           to_constant)
from .literals.base import (integers,
                            json_serializable_objects,
                            numbers,
                            objects,
                            real_numbers)
from .literals.factories import (to_iterables,
                                 to_lists,
                                 to_strings)

false_predicates = strategies.just(to_constant(False))
true_predicates = strategies.just(to_constant(True))
predicates = false_predicates | true_predicates
starting_maps = [identity, float, str, json.dumps]
suitable_maps = {identity: starting_maps,
                 float: starting_maps,
                 str: [identity, float, str, json.loads],
                 json.dumps: [identity, float, str, json.loads],
                 json.loads: starting_maps}
suitable_maps = dict(zip(suitable_maps.keys(),
                         map(strategies.sampled_from, suitable_maps.values())))
to_one_of_suitable_maps = suitable_maps.__getitem__
maps = strategies.sampled_from(starting_maps)
maps_arguments = (strategies.integers()
                  | strategies.floats(allow_nan=False,
                                      allow_infinity=False))
# "transparent" is an abbr. of "referential transparent"
transparent_functions = strategies.sampled_from([bool, complex, float,
                                                 identity, int,
                                                 json.dumps, json.loads, str])
paths_names_parts = to_strings(string.digits + string.ascii_letters + '_')
transparent_functions_args = {
    bool: strategies.tuples(objects),
    complex: strategies.tuples(numbers),
    float: strategies.tuples(real_numbers),
    identity: strategies.tuples(objects),
    int: strategies.tuples(integers),
    json.dumps: strategies.tuples(json_serializable_objects),
    json.loads: strategies.tuples(json_serializable_objects.map(json.dumps)),
    os.path.join: to_lists(paths_names_parts,
                           min_size=1).map(tuple),
    str: strategies.tuples(objects),
    sum: strategies.tuples(to_iterables(numbers)),
}
empty_dictionaries = strategies.fixed_dictionaries({})
transparent_functions_kwargs = {
    bool: empty_dictionaries,
    complex: empty_dictionaries,
    float: empty_dictionaries,
    identity: empty_dictionaries,
    int: empty_dictionaries,
    json.dumps: strategies.fixed_dictionaries(
            {'indent': strategies.integers(0, 10),
             'sort_keys': strategies.booleans()}),
    json.loads: strategies.fixed_dictionaries({
        'object_pairs_hook': strategies.none() | strategies.just(OrderedDict),
        'parse_float': strategies.none() | strategies.sampled_from([float,
                                                                    Decimal]),
        'parse_int': strategies.none() | strategies.sampled_from([int,
                                                                  float])}),
    os.path.join: empty_dictionaries,
    str: empty_dictionaries,
    sum: empty_dictionaries,
}
to_transparent_functions_args = transparent_functions_args.__getitem__
to_transparent_functions_kwargs = transparent_functions_kwargs.__getitem__
