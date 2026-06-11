# setup.py for historic_calculator.
#
# Unlike the distutils-based setup.py used in py23 (which only knew about
# the informational `requires=` keyword from PEP 314), this file uses
# *setuptools* and the `install_requires=` keyword. setuptools (released
# 2004) introduced real, enforceable runtime dependency declarations --
# the direct ancestor of every modern Python packaging tool.
from setuptools import setup

setup(
    name="historic_calculator",
    version="3.0.0",
    description="A tiny vector calculator using Numeric and setuptools.",
    package_dir={"": "src"},
    packages=["historic_calculator"],
    install_requires=[
        "Numeric",
    ],
    # setuptools 0.6c11 already supports `console_scripts` entry points,
    # which generate a launcher named `hist_calc` on the user's PATH at
    # install time. Wheels (PEP 427) do not exist yet in 2004 -- this
    # project is distributed as an sdist (`python setup.py sdist`).
    entry_points={
        "console_scripts": [
            "hist_calc = historic_calculator.main:main_cli",
        ],
    },
)
