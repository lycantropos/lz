import json

from hypothesis import strategies

from lz.functional import (identity,
                           to_constant)

false_predicates = strategies.just(to_constant(False))
true_predicates = strategies.just(to_constant(True))
predicates = false_predicates | true_predicates
suitable_maps = {identity: [identity, float, str, json.dumps],
                 float: [identity, float, str, json.dumps],
                 str: [identity, float, str, json.loads],
                 json.dumps: [identity, float, str, json.loads],
                 json.loads: [identity, float, str, json.dumps]}
suitable_maps = dict(zip(suitable_maps.keys(),
                         map(strategies.sampled_from, suitable_maps.values())))
to_one_of_suitable_maps = suitable_maps.__getitem__
maps = to_one_of_suitable_maps(json.loads)
next_maps = maps.flatmap(to_one_of_suitable_maps)
last_maps = next_maps.flatmap(to_one_of_suitable_maps)
maps_arguments = (strategies.integers()
                  | strategies.floats(allow_nan=False,
                                      allow_infinity=False))
