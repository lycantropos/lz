import io
from functools import partial
from operator import methodcaller
from typing import (AnyStr,
                    Iterable,
                    Optional,
                    Sequence,
                    Tuple,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Map)
from tests.configs import MAX_ITERABLES_SIZE

to_characters = strategies.characters
to_integers = strategies.integers
limit_max_size = partial(partial,
                         max_size=MAX_ITERABLES_SIZE)


def to_byte_arrays(*,
                   min_size: int = 0) -> SearchStrategy[bytearray]:
    return to_byte_strings(min_size).map(bytearray)


def to_byte_sequences(*,
                      min_size: int = 0
                      ) -> SearchStrategy[Union[bytearray, bytes]]:
    return (to_byte_arrays(min_size=min_size)
            | to_byte_strings(min_size=min_size))


def to_byte_streams(*,
                    min_size: int = 0
                    ) -> SearchStrategy[io.BytesIO]:
    return strategies.builds(io.BytesIO,
                             to_byte_strings(min_size))


to_byte_strings = limit_max_size(strategies.binary)
to_dictionaries = limit_max_size(strategies.dictionaries)
to_homogeneous_frozensets = limit_max_size(strategies.frozensets)


def to_homogeneous_iterables(elements: Optional[SearchStrategy[Domain]] = None,
                             *,
                             min_size: int = 0
                             ) -> SearchStrategy[Iterable[Domain]]:
    return (to_homogeneous_sequences(elements,
                                     min_size=min_size)
            | to_homogeneous_iterators(elements,
                                       min_size=min_size))


to_homogeneous_iterators = limit_max_size(strategies.iterables)
to_homogeneous_lists = limit_max_size(strategies.lists)


def to_homogeneous_sequences(elements: Optional[SearchStrategy[Domain]] = None,
                             *,
                             min_size: int = 0
                             ) -> SearchStrategy[Sequence[Domain]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size)
            | to_homogeneous_tuples(elements,
                                    min_size=min_size))


to_homogeneous_sets = limit_max_size(strategies.sets)


def to_homogeneous_tuples(elements: Optional[SearchStrategy[Domain]] = None,
                          *,
                          min_size: int = 0
                          ) -> SearchStrategy[Tuple[Domain, ...]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size)
            .map(tuple))


def to_iterables(elements: Optional[SearchStrategy[Domain]] = None,
                 *,
                 alphabet: SearchStrategy[str] = to_characters(),
                 min_size: int = 0
                 ) -> SearchStrategy[Iterable[Union[AnyStr, Domain]]]:
    return (to_byte_sequences(min_size=min_size)
            | to_byte_streams(min_size=min_size)
            | to_homogeneous_iterables(elements,
                                       min_size=min_size)
            | to_strings(alphabet,
                         min_size=min_size)
            | to_text_streams(alphabet,
                              min_size=min_size))


to_strings = limit_max_size(strategies.text)

supported_encodings = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp1006',
                       'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251',
                       'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256',
                       'cp1257', 'cp1258', 'cp273', 'cp424', 'cp437', 'cp500',
                       'cp65001', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852',
                       'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861',
                       'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869',
                       'cp874', 'cp875', 'cp932', 'cp949', 'cp950',
                       'euc_jis_2004', 'euc_jisx0213', 'euc_jp', 'euc_kr',
                       'gb18030', 'gb2312', 'gbk', 'hz',
                       'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                       'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                       'iso2022_kr', 'iso8859_10', 'iso8859_11', 'iso8859_13',
                       'iso8859_14', 'iso8859_15', 'iso8859_16', 'iso8859_2',
                       'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6',
                       'iso8859_7', 'iso8859_8', 'iso8859_9', 'johab',
                       'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'latin_1',
                       'mac_cyrillic', 'mac_greek', 'mac_iceland',
                       'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154',
                       'shift_jis', 'shift_jis_2004', 'shift_jisx0213',
                       'utf_16', 'utf_16_be', 'utf_16_le',
                       'utf_32', 'utf_32_be', 'utf_32_le',
                       'utf_7', 'utf_8', 'utf_8_sig']


@strategies.composite
def to_text_streams(draw: Map[SearchStrategy[Domain], Domain],
                    alphabet: SearchStrategy[str],
                    encodings: SearchStrategy[str] =
                    strategies.sampled_from(supported_encodings),
                    min_size: int = 0) -> io.TextIOWrapper:
    encoding = draw(encodings)
    byte_string = draw(to_strings(alphabet,
                                  min_size=min_size)
                       .map(methodcaller('encode', encoding, 'ignore')))
    byte_stream = io.BytesIO(byte_string)
    return io.TextIOWrapper(byte_stream,
                            encoding=encoding)
