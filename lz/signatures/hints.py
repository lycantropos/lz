from typing import (Any,
                    Dict)

Namespace = Dict[str, Any]

try:
    from types import MethodDescriptorType
except ImportError:
    MethodDescriptorType = type(list.append)
