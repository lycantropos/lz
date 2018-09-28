from setuptools import (find_packages,
                        setup)

import lz

project_base_url = 'https://github.com/lycantropos/lz/'

install_requires = [
    'mypy_extensions>=0.4.1',
    'typeshed>=0.0.1',
    'typing_extensions>=3.6.5',
]
setup_requires = [
    'pytest-runner>=4.2'
]
tests_require = [
    'pydevd>=1.4.0',  # debugging
    'pytest>=3.8.1',
    'pytest-cov>=2.6.0',
    'hypothesis>=3.73.1',
]

setup(name='lz',
      packages=find_packages(exclude=('tests',)),
      version=lz.__version__,
      description=lz.__doc__,
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      install_requires=install_requires,
      setup_requires=setup_requires,
      tests_require=tests_require)
