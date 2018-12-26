import io

from hypothesis import strategies

byte_strings = strategies.just(b'')
byte_arrays = strategies.builds(bytearray,
                                byte_strings)
byte_streams = strategies.builds(io.BytesIO,
                                 byte_strings)
dictionaries = strategies.builds(dict)
iterators = strategies.iterables(strategies.nothing())
lists = strategies.lists(strategies.nothing())
sets = strategies.sets(strategies.nothing())
strings = strategies.just('')
text_streams = strategies.builds(io.TextIOWrapper,
                                 byte_streams)
tuples = strategies.tuples()
byte_sequences = byte_arrays | byte_strings
sequences = byte_sequences | lists | strings | tuples
finite_iterables = dictionaries | sequences | sets
iterables = byte_streams | finite_iterables | iterators | text_streams
