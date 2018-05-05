lz
===========

[![](https://travis-ci.org/lycantropos/lz.svg?branch=master)](https://travis-ci.org/lycantropos/lz "Travis CI")
[![](https://codecov.io/gh/lycantropos/lz/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/lz "Codecov")
[![](https://img.shields.io/github/license/lycantropos/lz.svg)](https://github.com/lycantropos/lz/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/lz.svg)](https://badge.fury.io/py/lz "PyPI")

In what follows `python3` is an alias for `python3.5` or any later
version (`python3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions

```bash
python3 -m pip install --upgrade pip setuptools
```

### Release

Download and install the latest stable version from `PyPI` repository

```bash
python3 -m pip install --upgrade lz
```

### Developer

Download and install the latest version from `GitHub` repository

```bash
git clone https://github.com/lycantropos/lz.git
cd lz
python3 setup.py install
```

Bumping version
---------------

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version

```bash
bump2version --dry-run --verbose $VERSION
```

where `$VERSION` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version

```bash
bump2version --verbose $VERSION
```

**Note**: to avoid inconsistency between branches and pull requests,
bumping version should be merged into `master` branch as separate pull
request.

Running tests
-------------

Plain

```bash
python3 setup.py test
```

Inside `Docker` container

```bash
docker-compose up
```

Bash script (e.g. can be used in `Git` hooks)

```bash
./run-tests.sh
```

PowerShell script (e.g. can be used in `Git` hooks)

```powershell
.\run-tests.ps1
```
