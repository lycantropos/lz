from hypothesis import strategies

from lz.functional import to_constant

false_predicates = strategies.just(to_constant(False))
true_predicates = strategies.just(to_constant(True))
predicates = false_predicates | true_predicates
