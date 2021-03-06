from tests.strategies import (classes,
                              scalars,
                              to_homogeneous_sequences)
from tests.utils import is_pickleable


def supports_instance_checks(class_: type) -> bool:
    try:
        isinstance(None, class_)
    except TypeError:
        return False
    else:
        return True


classes = classes.filter(supports_instance_checks)
classes_sequences = to_homogeneous_sequences(classes)
pickleable_classes_sequences = to_homogeneous_sequences(classes
                                                        .filter(is_pickleable))
scalars = scalars
