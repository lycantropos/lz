from typing import (Any,
                    Iterable)

from lz import (left,
                right)
from lz.iterating import (first,
                          last,
                          slider)
from lz.replication import duplicate
from tests.utils import (capacity,
                         is_empty)


def test_base_case_capacity(empty_iterable: Iterable[Any],
                            slider_size: int) -> None:
    slide = slider(slider_size)

    result = slide(empty_iterable)

    assert capacity(result) == 1


def test_base_case_elements(empty_iterable: Iterable[Any],
                            slider_size: int) -> None:
    slide = slider(slider_size)

    result = slide(empty_iterable)

    assert all(map(is_empty, result))


def test_step_left_total_capacity(iterable: Iterable[Any],
                                  object_: Any,
                                  slider_size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(slider_size)
    attach = left.attacher(object_)

    result = slide(attach(target))

    assert 0 <= capacity(result) - capacity(slide(original)) <= 1


def test_step_left_elementwise_capacity(iterable: Iterable[Any],
                                        object_: Any,
                                        slider_size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(slider_size)
    attach = left.attacher(object_)

    result = slide(attach(target))

    assert all(0 <= capacity(element) <= slider_size
               for element in result)


def test_step_left_elements(iterable: Iterable[Any],
                            object_: Any,
                            slider_size: int) -> None:
    slide = slider(slider_size)
    attach = left.attacher(object_)

    result = slide(attach(iterable))

    assert first(first(result)) is object_


def test_step_right_total_capacity(iterable: Iterable[Any],
                                   object_: Any,
                                   slider_size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(slider_size)
    attach = right.attacher(object_)

    result = slide(attach(target))

    assert 0 <= capacity(result) - capacity(slide(original)) <= 1


def test_step_right_elementwise_capacity(iterable: Iterable[Any],
                                         object_: Any,
                                         slider_size: int) -> None:
    original, target = duplicate(iterable)
    slide = slider(slider_size)
    attach = right.attacher(object_)

    result = slide(attach(target))

    assert all(0 <= capacity(element) <= slider_size
               for element in result)


def test_step_right_elements(iterable: Iterable[Any],
                             object_: Any,
                             slider_size: int) -> None:
    slide = slider(slider_size)
    attach = right.attacher(object_)

    result = slide(attach(iterable))

    assert last(last(result)) is object_
