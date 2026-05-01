# setup.py for historic-calculator on Python 2.7.
#
# By the early 2010s the setuptools-based setup.py is the de-facto standard,
# pip is the user-facing installer, and projects routinely declare runtime
# dependencies in `install_requires=`. A pinned `requirements.txt` lives
# alongside this file so deployments can reproduce a known-good dependency
# set.
from setuptools import setup

setup(
    name="historic-calculator",
    version="4.0.0",
    description="A tiny vector calculator using NumPy and setuptools.",
    packages=["my_package"],
    install_requires=[
        "numpy",
    ],
)
