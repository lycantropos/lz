import builtins
import inspect
import platform
import string
import sys
from collections import abc
from types import ModuleType
from typing import (Dict,
                    List,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from tests.configs import MAX_ITERABLES_SIZE
from .factories import (to_byte_sequences,
                        to_byte_strings,
                        to_characters,
                        to_dictionaries,
                        to_homogeneous_frozensets,
                        to_homogeneous_iterables,
                        to_homogeneous_iterators,
                        to_homogeneous_lists,
                        to_homogeneous_sets,
                        to_homogeneous_tuples,
                        to_integers,
                        to_strings)

Serializable = Union[None, bool, float, int, str]
Serializable = Union[Dict[str, Serializable], List[Serializable]]

booleans = strategies.booleans()
integers = (booleans
            | strategies.integers())
real_numbers = (integers
                | strategies.floats(allow_nan=False,
                                    allow_infinity=False))
numbers = (real_numbers
           | strategies.complex_numbers(allow_nan=False,
                                        allow_infinity=False))
scalars = (strategies.none()
           | numbers
           | strategies.just(NotImplemented)
           | strategies.just(Ellipsis))

encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp1006',
             'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251',
             'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256',
             'cp1257', 'cp1258', 'cp273', 'cp424', 'cp437', 'cp500',
             'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855',
             'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862',
             'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874',
             'cp875', 'cp932', 'cp949', 'cp950', 'euc_jis_2004',
             'euc_jisx0213', 'euc_jp', 'euc_kr', 'gb18030',
             'gb2312', 'gbk', 'hz', 'iso2022_jp', 'iso2022_jp_1',
             'iso2022_jp_2', 'iso2022_jp_3', 'iso2022_jp_2004',
             'iso2022_jp_ext', 'iso2022_kr', 'iso8859_10',
             'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15',
             'iso8859_16', 'iso8859_2', 'iso8859_3', 'iso8859_4',
             'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8',
             'iso8859_9', 'johab', 'koi8_r', 'koi8_t', 'koi8_u',
             'kz1048', 'latin_1', 'mac_cyrillic', 'mac_greek',
             'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
             'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
             'utf_16', 'utf_16_be', 'utf_16_le', 'utf_32',
             'utf_32_be', 'utf_32_le', 'utf_8', 'utf_8_sig']
if sys.platform == 'win32' and platform.python_implementation() != 'PyPy':
    encodings.append('cp65001')
encodings = strategies.sampled_from(encodings)
byte_strings = encodings.flatmap(to_byte_strings)
strings = to_strings(to_characters())


def module_to_classes(module: ModuleType) -> List[type]:
    return list(filter(inspect.isclass,
                       vars(module).values()))


abstract_base_classes = strategies.sampled_from(module_to_classes(abc))
built_in_classes = strategies.sampled_from(module_to_classes(builtins))
classes = abstract_base_classes | built_in_classes

deferred_hashables = strategies.deferred(lambda: hashables)
deferred_objects = strategies.deferred(lambda: objects)
hashables = (scalars
             | byte_strings
             | strings
             | classes
             | to_homogeneous_frozensets(deferred_hashables)
             | to_homogeneous_iterators(deferred_objects)
             | to_homogeneous_tuples(deferred_hashables))
indices = strategies.integers(-MAX_ITERABLES_SIZE, MAX_ITERABLES_SIZE - 1)
slices_fields = strategies.none() | indices
slices = strategies.builds(slice,
                           slices_fields,
                           slices_fields,
                           slices_fields)
byte_sequences = encodings.flatmap(to_byte_sequences)
any_strings = strings | byte_sequences
iterables = (any_strings
             | to_homogeneous_iterables(deferred_objects))
sets = to_homogeneous_sets(hashables)
objects = (hashables
           | slices
           | iterables
           | sets
           | to_dictionaries(hashables, deferred_objects))
tuples = to_homogeneous_tuples(objects)
lists = to_homogeneous_lists(objects)


def extend_json(children: SearchStrategy[Serializable]
                ) -> SearchStrategy[Serializable]:
    return (strategies.lists(children)
            | to_dictionaries(to_strings(string.printable),
                              children))


json_serializable_objects = strategies.recursive(
        strategies.none()
        | real_numbers
        | to_strings(string.printable),
        extend_json)
positionals_arguments = tuples
keywords_arguments = to_dictionaries(strings, objects)

sortable_domains = [byte_sequences, real_numbers, sets, strings]
sortable_iterables = strategies.one_of(*map(to_homogeneous_iterables,
                                            sortable_domains))

iterables_sizes = to_integers(0, MAX_ITERABLES_SIZE)
