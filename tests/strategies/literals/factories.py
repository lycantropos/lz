import io
import locale
from functools import partial
from typing import (AnyStr,
                    IO,
                    Iterable,
                    Optional,
                    Sequence,
                    Tuple,
                    Union)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from lz.hints import Domain
from tests.configs import MAX_ITERABLES_SIZE

to_characters = strategies.characters
to_integers = strategies.integers
limit_max_size = partial(partial,
                         max_size=MAX_ITERABLES_SIZE)


def to_any_streams(encoding: Optional[str],
                   *,
                   min_size: int = 0) -> SearchStrategy[IO[AnyStr]]:
    return (to_byte_streams(encoding,
                            min_size=min_size)
            | to_text_streams(encoding,
                              min_size=min_size))


def to_byte_arrays(encoding: Optional[str],
                   *,
                   min_size: int = 0) -> SearchStrategy[bytearray]:
    return (to_byte_strings(encoding,
                            min_size=min_size)
            .map(bytearray))


def to_byte_sequences(encoding: Optional[str],
                      *,
                      min_size: int = 0
                      ) -> SearchStrategy[Union[bytearray, bytes]]:
    return (to_byte_arrays(encoding,
                           min_size=min_size)
            | to_byte_strings(encoding,
                              min_size=min_size))


def to_byte_streams(encoding: Optional[str],
                    *,
                    min_size: int = 0) -> SearchStrategy[Iterable[bytes]]:
    bytes_io_streams = strategies.builds(io.BytesIO,
                                         to_byte_sequences(encoding,
                                                           min_size=min_size))
    return (bytes_io_streams
            | strategies.builds(io.BufferedReader, bytes_io_streams))


def to_byte_strings(encoding: Optional[str],
                    *,
                    min_size: int = 0,
                    max_size: int = MAX_ITERABLES_SIZE
                    ) -> SearchStrategy[bytes]:
    if encoding is None:
        encoding = locale.getpreferredencoding(False)

    def to_decodable(byte_string: bytes) -> bytes:
        return (byte_string.decode(encoding, 'replace')
                .encode(encoding, 'replace'))

    def is_decodable(byte_string: bytes) -> bool:
        try:
            byte_string.decode(encoding)
        except UnicodeDecodeError:
            return False
        else:
            return True

    return (strategies.binary(min_size=min_size,
                              max_size=max_size)
            .map(to_decodable)
            .filter(is_decodable))


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


def to_byte_iterables(encoding: Optional[str],
                      *,
                      min_size: int = 0
                      ) -> SearchStrategy[Union[bytes,
                                                Iterable[bytes]]]:
    return (to_byte_sequences(encoding,
                              min_size=min_size)
            | to_byte_streams(encoding,
                              min_size=min_size))


to_strings = limit_max_size(strategies.text)


def to_text_streams(encoding: Optional[str],
                    *,
                    min_size: int = 0) -> io.TextIOWrapper:
    return strategies.builds(io.TextIOWrapper,
                             to_byte_streams(encoding,
                                             min_size=min_size),
                             encoding=strategies.just(encoding))
