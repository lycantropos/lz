import os
from itertools import repeat
from operator import (itemgetter,
                      truediv)
from pathlib import Path
from typing import (Iterator,
                    List)

from .functional import (compose,
                         unpack)
from .iterating import (flatmapper,
                        mapper)

INIT_MODULE_NAME = '__init__'


def find_files(directory: Path) -> Iterator[Path]:
    def to_paths(root: str, files: List[str]) -> Iterator[Path]:
        yield from map(truediv, repeat(Path(root)), files)

    finder = compose(flatmapper(unpack(to_paths)),
                     mapper(itemgetter(0, 2)),
                     os.walk)
    yield from finder(directory)
