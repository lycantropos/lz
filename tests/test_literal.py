from lz.literal import to_unique_object


def test_to_unique_object() -> None:
    first_object = to_unique_object()
    second_object = to_unique_object()

    assert first_object is first_object
    assert second_object is second_object
    assert first_object == first_object
    assert second_object == second_object
    assert first_object is not second_object
    assert first_object != second_object
