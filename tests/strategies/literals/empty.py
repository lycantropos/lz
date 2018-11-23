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
sequences = byte_arrays | byte_strings | lists | strings | tuples
iterables = byte_streams | iterators | sequences | text_streams
