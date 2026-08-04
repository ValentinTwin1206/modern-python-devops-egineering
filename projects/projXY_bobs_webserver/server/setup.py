from setuptools import setup

setup(
    name="internal-http-service-v2-new",
    version="2.4.13",
    description="New implementation of the internal HTTP service. (Originally created in 2017.)",
    author="Bob",
    license="Proprietary",
    url="http://legacy.internal.local",
    python_requires=">=3.8,<3.10",
    install_requires=[
        "requests==2.0.0",
        "urllib3==1.7.1",
        "certifi==2015.04.28",
        "chardet==2.1.1"
    ],
    zip_safe=False,
)