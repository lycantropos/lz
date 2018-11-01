class Unique:
    def __init__(self,
                 *,
                 name: str = None,
                 documentation: str = None) -> None:
        self.__name__ = name
        self.__doc__ = documentation

    def __repr__(self) -> str:
        result = '<' + type(self).__qualname__ + ' object'
        if self.__name__:
            result += ' "{name}"'.format(name=self.__name__)
        result += ' at {id}'.format(id=hex(id(self)))
        return result + '>'


to_unique_object = Unique
