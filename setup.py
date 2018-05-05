import lz
from lz.config import PROJECT_NAME
from setuptools import (find_packages,
                        setup)

project_base_url = 'https://github.com/lycantropos/lz/'

setup_requires = [
    'pytest-runner>=3.0'
]
tests_require = [
    'pydevd>=1.1.1',  # debugging
    'pytest>=3.3.0',
    'pytest-cov>=2.5.1',
    'hypothesis>=3.38.5',
]

setup(name=PROJECT_NAME,
      packages=find_packages(exclude=('tests',)),
      version=lz.__version__,
      description=lz.__doc__,
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      setup_requires=setup_requires,
      tests_require=tests_require)
