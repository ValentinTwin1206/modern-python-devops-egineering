from distutils.core import setup

setup(
    name="historic_calculator",
    version="1.0.0",
    description="A historical Python 1.6 application",
    package_dir={"": "src"},
    packages=["historic_calculator"],
    # distutils 1.6 has no entry-points concept, so we ship a real
    # launcher script and let `scripts=` install it onto PATH.
    scripts=["bin/hist_calc"],
)
