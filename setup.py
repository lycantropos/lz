from pathlib import Path

from setuptools import (find_packages,
                        setup)

import lz

project_base_url = 'https://github.com/lycantropos/lz/'

install_requires = Path('requirements.txt').read_text()
setup_requires = [
    'pytest-runner>=4.2',
]
tests_require = Path('requirements-tests.txt').read_text()

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
