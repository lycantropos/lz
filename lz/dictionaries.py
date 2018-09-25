from operator import methodcaller

from .functional import compose
from .iterating import flatmapper

merge = compose(dict,
                flatmapper(methodcaller('items')))
