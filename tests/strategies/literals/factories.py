import io
import sys
from collections import defaultdict
from functools import wraps
from operator import methodcaller
from typing import (AnyStr,
                    BinaryIO,
                    Callable,
                    IO,
                    Iterable,
                    Optional,
                    Sequence,
                    TextIO,
                    Tuple,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import Domain
from tests.configs import MAX_ITERABLES_SIZE
from tests.utils import encoding_to_bom

to_characters = strategies.characters
to_integers = strategies.integers


def limit_max_size(factory: Callable[..., SearchStrategy[Domain]]):
    @wraps(factory)
    def limited(*args, max_size: int = MAX_ITERABLES_SIZE, **kwargs
                ) -> SearchStrategy[Domain]:
        return factory(*args, max_size=max_size, **kwargs)

    return limited


@limit_max_size
def to_any_streams(encoding: str,
                   *,
                   min_size: int = 0,
                   max_size: Optional[int] = None
                   ) -> SearchStrategy[IO[AnyStr]]:
    return (to_byte_streams(encoding,
                            min_size=min_size,
                            max_size=max_size)
            | to_text_streams(encoding,
                              min_size=min_size,
                              max_size=max_size))


@limit_max_size
def to_byte_arrays(encoding: str,
                   *,
                   min_size: int = 0,
                   max_size: Optional[int] = None
                   ) -> SearchStrategy[bytearray]:
    return (to_byte_strings(encoding,
                            min_size=min_size,
                            max_size=max_size)
            .map(bytearray))


@limit_max_size
def to_byte_iterables(encoding: str,
                      *,
                      min_size: int = 0,
                      max_size: Optional[int] = None
                      ) -> SearchStrategy[Union[bytes,
                                                Iterable[bytes]]]:
    return (to_byte_sequences(encoding,
                              min_size=min_size,
                              max_size=max_size)
            | to_byte_streams(encoding,
                              min_size=min_size,
                              max_size=max_size))


@limit_max_size
def to_byte_sequences(encoding: str,
                      *,
                      min_size: int = 0,
                      max_size: Optional[int] = None
                      ) -> SearchStrategy[Union[bytearray, bytes]]:
    return (to_byte_arrays(encoding,
                           min_size=min_size,
                           max_size=max_size)
            | to_byte_strings(encoding,
                              min_size=min_size,
                              max_size=max_size))


@limit_max_size
def to_byte_streams(encoding: str,
                    *,
                    min_size: int = 0,
                    max_size: Optional[int] = None
                    ) -> SearchStrategy[BinaryIO]:
    bom = encoding_to_bom(encoding)

    min_size_without_bom = max(min_size - len(bom), 0)
    max_size_without_bom = max_size
    if max_size_without_bom is not None:
        max_size_without_bom = max(max_size_without_bom - len(bom), 0)

    def append_bom(byte_string: bytes) -> bytes:
        return bom + byte_string

    byte_sequences = (to_byte_sequences(encoding,
                                        min_size=min_size_without_bom,
                                        max_size=max_size_without_bom)
                      .map(append_bom))
    bytes_io_streams = strategies.builds(io.BytesIO,
                                         byte_sequences)
    return (bytes_io_streams
            | strategies.builds(io.BufferedReader, bytes_io_streams))


@limit_max_size
def to_byte_strings(encoding: str,
                    *,
                    min_size: int = 0,
                    max_size: Optional[int] = None
                    ) -> SearchStrategy[bytes]:
    length = encodings_lengths[encoding]
    min_characters_count = (min_size + length - 1) // length
    max_characters_count = max_size
    if max_characters_count is not None:
        max_characters_count = (max_characters_count + length - 1) // length
    return (strategies.lists(to_characters_bytes(encoding),
                             min_size=min_characters_count,
                             max_size=max_characters_count)
            .map(b''.join))


def to_characters_bytes(encoding: str,
                        *,
                        little_byte_order_suffix: str = '_le',
                        big_byte_order_suffix: str = '_be',
                        little_byte_order_name: str = 'little',
                        big_byte_order_name: str = 'big'
                        ) -> SearchStrategy[bytes]:
    unsupported_code_points = encodings_unsupported_code_points[encoding]

    def is_code_point_supported(code_point: int) -> bool:
        return code_point not in unsupported_code_points

    has_byte_order_suffix = encoding.endswith((big_byte_order_suffix,
                                               little_byte_order_suffix))
    if has_byte_order_suffix:
        byte_order = (big_byte_order_name
                      if encoding.endswith(big_byte_order_suffix)
                      else little_byte_order_name)
    else:
        byte_order = sys.byteorder
    length = encodings_lengths[encoding]
    to_bytes = methodcaller(int.to_bytes.__name__, length, byte_order)
    code_points = strategies.integers(0, 256 ** length - 1)
    return code_points.filter(is_code_point_supported).map(to_bytes)


encodings_lengths = defaultdict(lambda: 1,
                                {'utf_16': 2,
                                 'utf_16_be': 2,
                                 'utf_16_le': 2,
                                 'utf_32': 4,
                                 'utf_32_be': 4,
                                 'utf_32_le': 4})
encodings_unsupported_code_points = defaultdict(
        set,
        {'ascii': range(128, 256),
         'big5': range(128, 256),
         'big5hkscs': range(128, 256),
         'cp1250': {129, 131, 136, 144, 152},
         'cp1251': {152},
         'cp1252': {129, 141, 143, 144, 157},
         'cp1253': ({129, 136, 138} | set(range(140, 145)) | {152, 154}
                    | set(range(156, 160)) | {170, 210, 255}),
         'cp1254': {129} | set(range(141, 145)) | {157, 158},
         'cp1255': ({129, 138} | set(range(140, 145)) | {154}
                    | set(range(156, 160)) | {202} | set(range(217, 224))
                    | {251, 252, 255}),
         'cp1257': {129, 131, 136, 138, 140, 144, 152, 154, 156, 159, 161,
                    165},
         'cp1258': {129, 138, 141, 142, 143, 144, 154, 157, 158},
         'cp424': {112, 114, 115, 117, 118, 119, 128, 140, 141, 142, 154, 155,
                   156, 158, 170, 171, 172, 173, 174, 203, 204, 205, 206, 207,
                   219, 220, 221, 222, 223, 235, 236, 237, 238, 239, 251, 252,
                   253, 254},
         'cp856': ({155, 157} | set(range(159, 169)) | {173}
                   | set(range(181, 184)) | {198, 199} | set(range(208, 217))
                   | {222} | set(range(224, 230)) | set(range(231, 238))),
         'cp857': {213, 231, 242},
         'cp864': {155, 156, 159, 166, 167, 255},
         'cp869': set(range(128, 134)) | {135, 147, 148},
         'cp874': (set(range(129, 133)) | set(range(134, 145))
                   | set(range(152, 160)) | set(range(219, 223))
                   | set(range(252, 256))),
         'cp932': set(range(129, 253)) - set(range(160, 224)),
         'cp949': range(128, 256),
         'cp950': range(128, 256),
         'euc_jis_2004': range(128, 256),
         'euc_jisx0213': range(128, 256),
         'euc_jp': range(128, 256),
         'euc_kr': range(128, 256),
         'gb18030': range(128, 256),
         'gb2312': range(128, 256),
         'gbk': range(128, 256),
         'hz': {126} | set(range(128, 256)),
         'iso2022_jp': {27} | set(range(128, 256)),
         'iso2022_jp_1': {27} | set(range(128, 256)),
         'iso2022_jp_2': {27} | set(range(128, 256)),
         'iso2022_jp_3': {27} | set(range(128, 256)),
         'iso2022_jp_2004': {27} | set(range(128, 256)),
         'iso2022_jp_ext': {27} | set(range(128, 256)),
         'iso2022_kr': {27} | set(range(128, 256)),
         'iso8859_11': {219, 220, 221, 222, 252, 253, 254, 255},
         'iso8859_3': {165, 174, 190, 195, 208, 227, 240},
         'iso8859_6': (set(range(161, 164)) | set(range(165, 172))
                       | set(range(174, 187)) | set(range(188, 191)) | {192}
                       | set(range(219, 224)) | set(range(243, 256))),
         'iso8859_7': {174, 210, 255},
         'iso8859_8': {161} | set(range(191, 223)) | {251, 252, 255},
         'johab': set(range(128, 256)),
         'koi8_t': ({136, 143, 152, 154} | set(range(156, 161))
                    | {168, 169, 170, 175, 180, 184, 186, 188, 189, 190}),
         'kz1048': {152},
         'shift_jis': set(range(128, 256)) - set(range(161, 224)),
         'shift_jis_2004': set(range(128, 256)) - set(range(161, 224)),
         'shift_jisx0213': set(range(128, 256)) - set(range(161, 224)),
         'utf_16': range(0xd800, 0xe000),
         'utf_16_be': range(0xd800, 0xe000),
         'utf_16_le': range(0xd800, 0xe000),
         'utf_32': range(0x110000, 256 ** encodings_lengths['utf_32']),
         'utf_32_be': range(0x110000, 256 ** encodings_lengths['utf_32_be']),
         'utf_32_le': range(0x110000, 256 ** encodings_lengths['utf_32_le']),
         'utf_8': range(128, 256),
         'utf_8_sig': range(128, 256),
         'cp65001': range(128, 256),
         })

to_dictionaries = limit_max_size(strategies.dictionaries)
to_homogeneous_frozensets = limit_max_size(strategies.frozensets)


@limit_max_size
def to_homogeneous_iterables(elements: Optional[SearchStrategy[Domain]] = None,
                             *,
                             min_size: int = 0,
                             max_size: Optional[int] = None
                             ) -> SearchStrategy[Iterable[Domain]]:
    return (to_homogeneous_sequences(elements,
                                     min_size=min_size,
                                     max_size=max_size)
            | to_homogeneous_iterators(elements,
                                       min_size=min_size,
                                       max_size=max_size))


to_homogeneous_iterators = limit_max_size(strategies.iterables)
to_homogeneous_lists = limit_max_size(strategies.lists)


@limit_max_size
def to_homogeneous_sequences(elements: Optional[SearchStrategy[Domain]] = None,
                             *,
                             min_size: int = 0,
                             max_size: Optional[int] = None
                             ) -> SearchStrategy[Sequence[Domain]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size,
                                 max_size=max_size)
            | to_homogeneous_tuples(elements,
                                    min_size=min_size,
                                    max_size=max_size))


to_homogeneous_sets = limit_max_size(strategies.sets)


@limit_max_size
def to_homogeneous_tuples(elements: Optional[SearchStrategy[Domain]] = None,
                          *,
                          min_size: int = 0,
                          max_size: Optional[int] = None
                          ) -> SearchStrategy[Tuple[Domain, ...]]:
    return (to_homogeneous_lists(elements,
                                 min_size=min_size,
                                 max_size=max_size)
            .map(tuple))


to_strings = limit_max_size(strategies.text)


@limit_max_size
def to_text_streams(encoding: str,
                    *,
                    min_size: int = 0,
                    max_size: Optional[int] = None
                    ) -> SearchStrategy[TextIO]:
    encoding_length = encodings_lengths[encoding]
    bom = encoding_to_bom(encoding)
    byte_stream_min_size = min_size * encoding_length + len(bom)
    byte_stream_max_size = max_size
    if byte_stream_max_size is not None:
        byte_stream_max_size = (byte_stream_max_size * encoding_length
                                + len(bom))
    return strategies.builds(io.TextIOWrapper,
                             to_byte_streams(encoding,
                                             min_size=byte_stream_min_size,
                                             max_size=byte_stream_max_size),
                             encoding=strategies.just(encoding))
