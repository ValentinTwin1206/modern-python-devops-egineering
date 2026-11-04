# setup.py for historic_calculator on Python 2.7.
#
# By the early 2010s the setuptools-based setup.py is the de-facto standard,
# pip is the user-facing installer, and projects routinely declare runtime
# dependencies in `install_requires=`. A pinned `requirements.txt` lives
# alongside this file so deployments can reproduce a known-good dependency
# set.
from setuptools import setup

setup(
    name="historic_calculator",
    version="4.0.0",
    description="A tiny vector calculator using NumPy and setuptools.",
    package_dir={"": "src"},
    packages=["historic_calculator"],
    install_requires=[
        "numpy",
    ],
    # setuptools provides a `console_scripts` entry point that installs
    # a `hist_calc` launcher on the user's PATH. The 2010-era 2.7 layout
    # predates wheels (PEP 427, 2012) so this project is distributed as
    # an sdist (`python setup.py sdist`).
    entry_points={
        "console_scripts": [
            "hist_calc = historic_calculator.main:main_cli",
        ],
    },
)
