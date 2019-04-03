from keyword import iskeyword
from string import ascii_letters

from hypothesis import strategies

from lz.logical import negate

identifiers_characters = strategies.sampled_from(ascii_letters + '_')
identifiers = (strategies.text(identifiers_characters,
                               min_size=1)
               .filter(str.isidentifier)
               .filter(negate(iskeyword)))
