from typing import (BinaryIO,
                    Callable,
                    Dict,
                    Tuple,
                    TypeVar,
                    Union)

from hypothesis.searchstrategy import SearchStrategy

from lz.hints import (Domain,
                      Range)

ByteStreamWithBatchParameters = Tuple[BinaryIO, bytes, Tuple[int, int]]
Intermediate = TypeVar('Intermediate')
ByteSequence = Union[bytearray, bytes]
Args = Tuple[Domain, ...]
Kwargs = Dict[str, Domain]
Function = Callable[..., Range]
FunctionCall = Tuple[Function, Args, Kwargs]
PartitionedFunctionCall = Tuple[Function,
                                Tuple[Args, Args],
                                Tuple[Kwargs, Kwargs]]
Strategy = SearchStrategy
