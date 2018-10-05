import json

from hypothesis import strategies

from lz.functional import (identity,
                           to_constant)

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
