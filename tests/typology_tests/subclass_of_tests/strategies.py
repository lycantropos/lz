from tests.strategies import (classes,
                              to_homogeneous_sequences)
from tests.utils import is_pickleable


def supports_instance_and_subclass_checks(cls: type) -> bool:
    try:
        isinstance(None, cls)
        issubclass(cls, cls)
    except TypeError:
        return False
    else:
        return True


classes = classes.filter(supports_instance_and_subclass_checks)
classes_sequences = to_homogeneous_sequences(classes)
pickleable_classes_sequences = to_homogeneous_sequences(classes
                                                        .filter(is_pickleable))
