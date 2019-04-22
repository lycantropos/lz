from pathlib import Path

from setuptools import (find_packages,
                        setup)

import lz

project_base_url = 'https://github.com/lycantropos/lz/'

install_requires = [
    'paradigm>=0.2.4',
    'reprit>=0.0.1',
    'typing_extensions>=3.6.5',
]
setup_requires = [
    'pytest-runner>=4.2'
]
tests_require = [
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=4.0.0',
]

setup(name='lz',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      version=lz.__version__,
      description=lz.__doc__,
      long_description=Path('README.md').read_text(),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5.3',
      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require)
