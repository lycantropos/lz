import builtins
import inspect
import json
import os
import random
import string
import textwrap
from collections import (OrderedDict,
                         abc)
from decimal import Decimal
from functools import (partial,
                       reduce,
                       singledispatch)
from operator import (add,
                      and_,
                      or_,
                      sub,
                      xor)
from types import ModuleType
from typing import (Any,
                    Callable,
                    Container,
                    Dict,
                    List,
                    Sequence,
                    Tuple)

from hypothesis import strategies
from paradigm import (models,
                      signatures)

from lz.functional import (identity,
                           to_constant)
from lz.hints import (Domain,
                      Map,
                      Range)
from lz.logical import negate
from lz.typology import instance_of
from tests.hints import (Args,
                         Function,
                         FunctionCall,
                         Kwargs,
                         PartitionedFunctionCall,
                         Strategy)
from .literals import empty
from .literals.base import (byte_sequences,
                            byte_sequences_with_encodings,
                            integers,
                            json_serializable_objects,
                            lists,
                            numbers,
                            real_numbers,
                            scalars,
                            sets,
                            sortable_domains,
                            strings,
                            strings_with_encodings,
                            tuples)
from .literals.factories import to_homogeneous_tuples
from .utils import identifiers

false_predicates = strategies.just(to_constant(False))
true_predicates = strategies.just(to_constant(True))


def module_to_classes(module: ModuleType) -> List[type]:
    return list(filter(inspect.isclass,
                       vars(module).values()))


abstract_base_classes = strategies.sampled_from(module_to_classes(abc))
built_in_classes = strategies.sampled_from(module_to_classes(builtins))
classes = abstract_base_classes | built_in_classes
is_instance_predicates = classes.map(instance_of)
predicates = false_predicates | true_predicates | is_instance_predicates
predicates_arguments = scalars
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
maps_arguments = (strategies.integers()
                  | strategies.floats(allow_nan=False,
                                      allow_infinity=False))


def extend_suitable_maps(maps_tuples: Strategy[Tuple[Map, ...]]
                         ) -> Strategy[Tuple[Map, ...]]:
    def expand(maps_tuple: Tuple[Map, ...]) -> Strategy[Tuple[Map, ...]]:
        return strategies.tuples(to_one_of_suitable_maps(maps_tuple[0]),
                                 *map(strategies.just, maps_tuple))

    return maps_tuples.flatmap(expand)


suitable_maps = strategies.recursive(strategies.tuples(maps),
                                     extend_suitable_maps)


def is_various(sequence: Sequence) -> bool:
    return len(sequence) > 1


various_suitable_maps = suitable_maps.filter(is_various)
# "transparent" is an abbr. of "referential transparent"
non_variadic_transparent_functions = strategies.sampled_from([bool, bytes,
                                                              complex, float,
                                                              identity,
                                                              int, str,
                                                              textwrap.indent])
variadic_transparent_functions = strategies.sampled_from([json.dumps,
                                                          json.loads,
                                                          os.path.join])
transparent_functions = (non_variadic_transparent_functions
                         | variadic_transparent_functions)
paths_names_parts = strategies.text(
        strategies.sampled_from(string.digits + string.ascii_letters + '_'))
to_transparent_function_args = {
    bool: strategies.tuples(scalars),
    bytes: strings_with_encodings,
    complex: strategies.tuples(numbers),
    float: strategies.tuples(real_numbers),
    identity: strategies.tuples(scalars),
    int: strategies.tuples(integers),
    json.dumps: strategies.tuples(json_serializable_objects),
    json.loads: strategies.tuples(json_serializable_objects.map(json.dumps)),
    os.path.join: to_homogeneous_tuples(paths_names_parts,
                                        min_size=1),
    str: byte_sequences_with_encodings,
    textwrap.indent: strategies.tuples(strings, strings),
}.__getitem__
to_transparent_function_kwargs = {
    bool: empty.dictionaries,
    bytes: empty.dictionaries,
    complex: empty.dictionaries,
    float: empty.dictionaries,
    identity: empty.dictionaries,
    int: empty.dictionaries,
    json.dumps: strategies.fixed_dictionaries({
        'indent': strategies.integers(0, 10),
        'sort_keys': strategies.just(True)}),
    json.loads: strategies.fixed_dictionaries({
        'object_pairs_hook': (strategies.none()
                              | strategies.just(OrderedDict)),
        'parse_float': (strategies.none()
                        | strategies.sampled_from([float, Decimal])),
        'parse_int': (strategies.none()
                      | strategies.sampled_from([int, float]))}),
    os.path.join: empty.dictionaries,
    str: empty.dictionaries,
    textwrap.indent: empty.dictionaries,
}.__getitem__
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
    (max, byte_sequences): empty.byte_sequences,
    (max, real_numbers): strategies.just(float('-inf')),
    (max, sets): empty.sets,
    (max, strings): empty.strings,
    (min, byte_sequences): empty.byte_sequences,
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


def to_transparent_functions_calls(function: Function
                                   ) -> Strategy[FunctionCall]:
    return strategies.tuples(strategies.just(function),
                             to_transparent_function_args(function),
                             to_transparent_function_kwargs(function))


def to_transparent_functions_calls_with_invalid_args(
        function: Function) -> Strategy[FunctionCall]:
    return strategies.tuples(strategies.just(function),
                             to_invalid_args(function),
                             to_transparent_function_kwargs(function))


def to_transparent_functions_calls_with_invalid_kwargs(
        function: Function) -> Strategy[FunctionCall]:
    return strategies.tuples(strategies.just(function),
                             to_transparent_function_args(function),
                             to_invalid_kwargs(function))


non_variadic_transparent_functions_calls_with_invalid_args = (
    non_variadic_transparent_functions.flatmap(
            to_transparent_functions_calls_with_invalid_args))
non_variadic_transparent_functions_calls_with_invalid_kwargs = (
    non_variadic_transparent_functions.flatmap(
            to_transparent_functions_calls_with_invalid_kwargs))
transparent_functions_calls = (transparent_functions
                               .flatmap(to_transparent_functions_calls))


def partition_call(call: FunctionCall) -> Strategy[PartitionedFunctionCall]:
    function, args, kwargs = call

    def partition_args(args_position: int) -> Tuple[Args, Args]:
        return args[:args_position], args[args_position:]

    def partition_kwargs(first_keys: Container[str]) -> Tuple[Kwargs, Kwargs]:
        return ({key: value
                 for key, value in kwargs.items()
                 if key in first_keys},
                {key: value
                 for key, value in kwargs.items()
                 if key not in first_keys})

    args_partitions = strategies.integers(0, len(args)).map(partition_args)
    kwargs_partitions = (strategies.integers(0, len(kwargs))
                         .map(partial(random.sample, kwargs.keys()))
                         .map(partition_kwargs))
    return strategies.tuples(strategies.just(function),
                             args_partitions, kwargs_partitions)


partitioned_transparent_functions_calls = (transparent_functions_calls
                                           .flatmap(partition_call))


def to_invalid_args(function: Callable[..., Any],
                    *,
                    values: Strategy[Domain] = strategies.none()
                    ) -> Strategy[Tuple[Domain, ...]]:
    signature = signatures.factory(function)
    count = signature_to_max_positionals_count(signature) + 1
    return to_homogeneous_tuples(values,
                                 min_size=count)


def to_invalid_kwargs(function: Callable[..., Any],
                      *,
                      values: Strategy[Domain] = strategies.none()
                      ) -> Strategy[Dict[str, Domain]]:
    signature = signatures.factory(function)
    keywords = signature_to_keywords_union(signature)
    is_unexpected = negate(keywords.__contains__)
    return (strategies.dictionaries(identifiers.filter(is_unexpected), values)
            .filter(bool))


@singledispatch
def signature_to_max_positionals_count(signature: models.Base) -> int:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@signature_to_max_positionals_count.register(models.Plain)
def plain_signature_to_max_positionals_count(signature: models.Plain) -> int:
    positionals = (signature.parameters_by_kind[
                       models.Parameter.Kind.POSITIONAL_ONLY]
                   + signature.parameters_by_kind[
                       models.Parameter.Kind.POSITIONAL_OR_KEYWORD])
    return len(positionals)


@signature_to_max_positionals_count.register(models.Overloaded)
def overloaded_signature_to_max_positionals_count(signature: models.Overloaded
                                                  ) -> int:
    return max(map(signature_to_max_positionals_count, signature.signatures),
               default=0)


@singledispatch
def signature_to_keywords_union(signature: models.Base
                                ) -> Dict[str, models.Parameter]:
    raise TypeError('Unsupported signature type: {type}.'
                    .format(type=type(signature)))


@signature_to_keywords_union.register(models.Plain)
def plain_signature_to_keywords_union(signature: models.Plain
                                      ) -> Dict[str, models.Parameter]:
    keywords = (signature.parameters_by_kind[
                    models.Parameter.Kind.POSITIONAL_OR_KEYWORD]
                + signature.parameters_by_kind[
                    models.Parameter.Kind.KEYWORD_ONLY])
    return models.to_parameters_by_name(keywords)


@signature_to_keywords_union.register(models.Overloaded)
def overloaded_signature_to_keywords_union(signature: models.Overloaded
                                           ) -> Dict[str, models.Parameter]:
    if not signature.signatures:
        return {}

    def unite(left_dictionary: Dict[Domain, Range],
              right_dictionary: Dict[Domain, Range]) -> Dict[Domain, Range]:
        return {**left_dictionary, **right_dictionary}

    return reduce(unite,
                  map(signature_to_keywords_union, signature.signatures))
