from typing import Any

from hypothesis.searchstrategy import SearchStrategy


def example(strategy: SearchStrategy) -> Any:
    return strategy.example()
