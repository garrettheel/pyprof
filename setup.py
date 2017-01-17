import os
import sys

from setuptools import setup, find_packages

setup(
    name='pyprof',
    version='0.1',
    packages=find_packages(),
    url='http://github.com/garrettheel/pyprof',
    author='',
    description='',
    zip_safe=False,
    install_requires=[
        'yappi',
        'gevent>=1.0',
    ],
)
