# setup.py for historic-calculator.
#
# Unlike the distutils-based setup.py used in py23 (which only knew about
# the informational `requires=` keyword from PEP 314), this file uses
# *setuptools* and the `install_requires=` keyword. setuptools (released
# 2004) introduced real, enforceable runtime dependency declarations --
# the direct ancestor of every modern Python packaging tool.
from setuptools import setup

setup(
    name="historic-calculator",
    version="3.0.0",
    description="A tiny vector calculator using Numeric and setuptools.",
    packages=["my_package"],
    install_requires=[
        "Numeric",
    ],
)
