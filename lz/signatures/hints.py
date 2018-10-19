from typing import (Any,
                    Dict)

Namespace = Dict[str, Any]

try:
    from types import MethodDescriptorType
except ImportError:
    MethodDescriptorType = type(list.append)
try:
    from types import WrapperDescriptorType
except ImportError:
    WrapperDescriptorType = type(list.__init__)
