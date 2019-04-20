from typing import (AnyStr,
                    BinaryIO,
                    Callable,
                    Dict,
                    IO,
                    Sequence,
                    Tuple,
                    TypeVar,
                    Union)

from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Map,
                      Range)

ByteStreamWithBatchParameters = Tuple[BinaryIO, bytes, Tuple[int, int]]
StreamWithReverseParameters = Tuple[IO, AnyStr, Tuple[int, AnyStr, bool]]
Intermediate = TypeVar('Intermediate')
ByteSequence = Union[bytearray, bytes]
Args = Tuple[Domain, ...]
Kwargs = Dict[str, Domain]
Function = Callable[..., Range]
FunctionCall = Tuple[Function, Args, Kwargs]
PartitionedFunctionCall = Tuple[Function,
                                Tuple[Args, Args],
                                Tuple[Kwargs, Kwargs]]
CombinationCall = Tuple[Sequence[Map], Sequence[Domain]]
CompositionCall = Tuple[Tuple[Map[Domain, Intermediate], ...], Domain]
Strategy = SearchStrategy
