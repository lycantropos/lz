from typing import (AnyStr,
                    BinaryIO,
                    Callable,
                    Dict,
                    IO,
                    Iterable,
                    Sequence,
                    Tuple,
                    TypeVar,
                    Union)

from hypothesis.strategies import SearchStrategy

Domain = TypeVar('Domain')
Range = TypeVar('Range')
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
LeftProjector = Callable[[Range, Domain], Range]
LeftAccumulatorCall = Tuple[LeftProjector, Range, Iterable[Domain]]
LeftFolderCall = Tuple[LeftProjector, Range, Iterable[Domain]]
RightProjector = Callable[[Domain, Range], Range]
RightAccumulatorCall = Tuple[LeftProjector, Range, Sequence[Domain]]
RightFolderCall = Tuple[RightProjector, Range, Sequence[Domain]]
CleavageCall = Tuple[Tuple[Callable[[Domain], Intermediate], ...], Domain]
CombinationCall = Tuple[Sequence[Callable[[Domain], Range]], Sequence[Domain]]
CompositionCall = Tuple[Tuple[Callable[[Domain], Intermediate], ...], Domain]
Strategy = SearchStrategy
