from distutils.core import setup

setup(
    name="historic_calculator",
    version="2.0.0",
    description="A historical Python 2.3 application",
    package_dir={"": "src"},
    packages=["historic_calculator"],
    requires=["Numeric==24.2"],
    # distutils in Python 2.3 has no entry-points concept, so we ship
    # a real launcher script and let `scripts=` install it onto PATH.
    scripts=["bin/hist_calc"],
)
