from operator import methodcaller

from lz.functional import compose
from lz.iterating import flatmapper

merge = compose(dict,
                flatmapper(methodcaller('items')))
