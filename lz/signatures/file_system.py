import os
from itertools import repeat
from operator import (itemgetter,
                      truediv)
from pathlib import Path
from typing import (Iterator,
                    List)

from lz.functional import (compose,
                           pack)
from lz.iterating import (flatmapper,
                          mapper)

INIT_MODULE_NAME = '__init__'


def find_files(directory: Path) -> Iterator[Path]:
    def to_paths(root: str, files: List[str]) -> Iterator[Path]:
        yield from map(truediv, repeat(Path(root)), files)

    finder = compose(flatmapper(pack(to_paths)),
                     mapper(itemgetter(0, 2)),
                     os.walk,
                     str)
    yield from finder(directory)
