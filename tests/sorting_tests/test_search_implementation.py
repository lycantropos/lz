import pytest

from lz.sorting import search_implementation


def test_search_registered_algorithm(registered_sorting_algorithm: str
                                     ) -> None:
    result = search_implementation(registered_sorting_algorithm)

    assert callable(result)


def test_search_unregistered_algorithm(unregistered_sorting_algorithm: str
                                       ) -> None:
    with pytest.raises(LookupError):
        search_implementation(unregistered_sorting_algorithm)
