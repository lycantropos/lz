lz
==

[![](https://travis-ci.org/lycantropos/lz.svg?branch=master)](https://travis-ci.org/lycantropos/lz "Travis CI")
[![](https://ci.appveyor.com/api/projects/status/github/lycantropos/lz?branch=master&svg=true)](https://ci.appveyor.com/project/lycantropos/lz "AppVeyor")
[![](https://codecov.io/gh/lycantropos/lz/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/lz "Codecov")
[![](https://readthedocs.org/projects/lz/badge/?version=latest)](https://lz.readthedocs.io/en/latest "Documentation")
[![](https://img.shields.io/github/license/lycantropos/lz.svg)](https://github.com/lycantropos/lz/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/lz.svg)](https://badge.fury.io/py/lz "PyPI")

In what follows 
- `python` is an alias for `python3.5` or any later
version (`python3.6` and so on),
- `pypy` is an alias for `pypy3.5` or any later
version (`pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:

- with `CPython`
  ```bash
  python -m pip install --upgrade pip setuptools
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade pip setuptools
  ```

### User

Download and install the latest stable version from `PyPI` repository:

- with `CPython`
  ```bash
  python -m pip install --upgrade lz
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade lz
  ```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/lz.git
cd lz
```

Install:
- with `CPython`
  ```bash
  python setup.py install
  ```
- with `PyPy`
  ```bash
  pypy setup.py install
  ```

Usage 
----- 
 
`lz` provides a bunch of utilities for working with functions, predicates & iterables such as

1. [function composition](https://en.wikipedia.org/wiki/Function_composition)
    ```python
    >>> from lz.functional import compose
    >>> sum_of_first_n_natural_numbers = compose(sum, range)
    >>> sum_of_first_n_natural_numbers(10)
    45

    ```

2. [currying](https://en.wikipedia.org/wiki/Currying)
    ```python
    >>> from lz.functional import curry 
    >>> curried_power = curry(pow) 
    >>> two_to_power = curried_power(2) 
    >>> two_to_power(10)
    1024

    ```

3. flipping positional parameters order
    ```python
    >>> from lz.functional import flip
    >>> flipped_power = flip(pow)
    >>> flipped_power(2, 4)
    16

    ```

4. packing function's arguments
    ```python
    >>> from lz.functional import pack
    >>> packed_int = pack(int)
    >>> packed_int(['10'])
    10
    >>> packed_int(['10'], {'base': 2})
    2

    ```

5. left [partial application](https://en.wikipedia.org/wiki/Partial_application)
    ```python
    >>> from lz import left
    >>> count_from_zero_to = left.applier(range, 0)
    >>> list(count_from_zero_to(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    ```

6. right [partial application](https://en.wikipedia.org/wiki/Partial_application)
    ```python
    >>> from lz import right
    >>> square = right.applier(pow, 2)
    >>> square(10)
    100

    ```

7. [negating](https://en.wikipedia.org/wiki/Negation) predicate
    ```python
    >>> from lz.logical import negate
    >>> false_like = negate(bool)
    >>> false_like([])
    True
    >>> false_like([0])
    False

    ```

8. [conjoining](https://en.wikipedia.org/wiki/Logical_conjunction) predicates
    ```python
    >>> from lz.logical import conjoin
    >>> is_valid_constant_identifier = conjoin(str.isupper, str.isidentifier)
    >>> is_valid_constant_identifier('SECOND_SECTION')
    True
    >>> is_valid_constant_identifier('2ND_SECTION')
    False

    ```

9. [disjoining](https://en.wikipedia.org/wiki/Logical_disjunction) predicates
    ```python
    >>> from lz.logical import disjoin
    >>> alphabetic_or_numeric = disjoin(str.isalpha, str.isnumeric)
    >>> alphabetic_or_numeric('Hello')
    True
    >>> alphabetic_or_numeric('42')
    True
    >>> alphabetic_or_numeric('Hello42')
    False

    ```

10. [exclusive disjoining](https://en.wikipedia.org/wiki/Exclusive_or) predicates
    ```python
    >>> from lz.logical import exclusive_disjoin
    >>> from keyword import iskeyword
    >>> valid_object_name = exclusive_disjoin(str.isidentifier, iskeyword)
    >>> valid_object_name('valid_object_name')
    True
    >>> valid_object_name('_')
    True
    >>> valid_object_name('1')
    False
    >>> valid_object_name('lambda')
    False

    ```

11. reversing sequences and any string streams
    ```python
    >>> from lz.reversal import reverse
    >>> list(reverse(range(10)))
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> import io
    >>> list(reverse(io.BytesIO(b'Hello\nWorld!')))
    [b'World!', b'Hello\n']

    ```

12. chunking iterable
    ```python
    >>> from lz.iterating import chopper
    >>> to_triplets = chopper(3)
    >>> list(map(tuple, to_triplets(range(10))))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

    ```

13. sliding over iterable
    ```python
    >>> from lz.iterating import slider
    >>> slide_pairwise = slider(2)
    >>> list(slide_pairwise(range(10)))
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
 
    ```

14. [interleaving](https://en.wikipedia.org/wiki/Interleave_sequence) iterables
    ```python
    >>> from lz.iterating import interleave
    >>> list(interleave([range(10), range(10, 20)]))
    [0, 10, 1, 11, 2, 12, 3, 13, 4, 14, 5, 15, 6, 16, 7, 17, 8, 18, 9, 19]
  
    ```

15. iterable [transposition](https://en.wikipedia.org/wiki/Transpose)
    ```python
    >>> from lz.transposition import transpose
    >>> list(map(tuple, transpose(zip(range(10), range(10, 20)))))
    [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)]
 
    ```

16. iterable duplication
    ```python
    >>> from lz.replication import duplicate
    >>> list(map(tuple, duplicate(range(10))))
    [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
  
    ```

and [many more](https://lz.readthedocs.io/en/latest).

Development
-----------

### Building docs

Install project in editable mode

- with `CPython`
  ```bash
  python -m pip install -e .
  ```
- with `PyPy`
  ```bash
  pypy -m pip install -e .
  ```

Install docs requirements

- with `CPython`
  ```bash
  python -m pip install -r docs/requirements.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install -r docs/requirements.txt
  ```

Build docs
```bash
cd docs
make html
```

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose --tag release
```

Bump version
```bash
bump2version --verbose --tag release
```

This will set version to `major.minor.patch` and add `Git` tag.

#### Notes

To avoid inconsistency between branches and pull requests,
bumping version should be merged into `master` branch as separate pull
request.

### Running tests

Plain:
- with `CPython`
  ```bash
  python setup.py test
  ```
- with `PyPy`
  ```bash
  pypy setup.py test
  ```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```


`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
