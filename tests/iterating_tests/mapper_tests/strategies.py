from tests.strategies import (empty,
                              maps,
                              maps_arguments,
                              to_homogeneous_iterables)

empty_iterables = empty.iterables
maps = maps
maps_arguments_iterables = to_homogeneous_iterables(maps_arguments)
non_empty_maps_arguments_iterables = to_homogeneous_iterables(maps_arguments,
                                                              min_size=1)
