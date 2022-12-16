import io
import os
import platform
from collections import abc
from functools import partial
from typing import (Any,
                    Dict,
                    Hashable,
                    Iterable,
                    TextIO)

import pytest
from hypothesis import (HealthCheck,
                        settings)

from lz.replication import replicate

on_azure_pipelines = bool(os.getenv('TF_BUILD', False))
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=((settings.default.max_examples
                                         // (1 + 4 * is_pypy))
                                        if on_azure_pipelines
                                        else 10**4),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow],
                          verbosity=2)


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
    replicate_iterable = replicate.dispatch(abc.Iterable)

    def replicate_sized(object_: Any,
                        *,
                        count: int) -> Iterable[Any]:
        yield from map(type(object_), replicate_iterable(object_,
                                                         count=count))

    replicate.register(bytearray, replicate_sized)
    replicate.register(frozenset, replicate_sized)
    replicate.register(list, replicate_sized)
    replicate.register(set, replicate_sized)

    def replicate_dictionary(object_: Dict[Hashable, Any],
                             *,
                             count: int) -> Iterable[Dict[Hashable, Any]]:
        yield from map(dict, replicate_iterable(object_.items(),
                                                count=count))

    replicate.register(dict, replicate_dictionary)
