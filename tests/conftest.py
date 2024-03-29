import io
import os
import sys
from datetime import timedelta
from functools import partial
from typing import (Iterable,
                    TextIO)

import pytest
from hypothesis import settings

from lz.replication import replicate

on_ci = bool(os.getenv('CI', False))
is_pypy = sys.implementation.name == 'pypy'
max_examples = (settings.default.max_examples // (4 + is_pypy)
                if on_ci
                else settings.default.max_examples)
settings.register_profile('default',
                          deadline=(timedelta(hours=1) / max_examples
                                    if on_ci
                                    else None),
                          max_examples=max_examples)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session,
                         exitstatus: pytest.ExitCode) -> None:
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK


@pytest.fixture(scope='session',
                autouse=True)
def patch_replication() -> None:
    def replicate_byte_buffer(object_: io.BytesIO,
                              *,
                              count: int) -> Iterable[io.BytesIO]:
        yield from map(io.BytesIO, replicate(object_.getvalue(),
                                             count=count))

    replicate.register(io.BytesIO, replicate_byte_buffer)

    def replicate_byte_stream(object_: io.BufferedReader,
                              *,
                              count: int) -> Iterable[io.BufferedReader]:
        yield from map(io.BufferedReader, replicate(object_.raw,
                                                    count=count))

    replicate.register(io.BufferedReader, replicate_byte_stream)

    def replicate_text_stream(object_: TextIO,
                              *,
                              count: int) -> Iterable[TextIO]:
        yield from map(partial(io.TextIOWrapper,
                               encoding=object_.encoding),
                       replicate(object_.buffer,
                                 count=count))

    replicate.register(io.TextIOWrapper, replicate_text_stream)
