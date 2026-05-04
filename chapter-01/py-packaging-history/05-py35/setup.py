# setup.py for historic_calculator on Python 3.5 (2016 era).
#
# As of setuptools 30.3.0 (released December 8, 2016) every piece of
# project metadata can live declaratively in setup.cfg, leaving setup.py
# as a single-line entry point. Older setuptools releases still need an
# imperative `setup(...)` call, so a thin shim keeps backwards
# compatibility.
from setuptools import setup

setup()
