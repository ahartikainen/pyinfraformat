from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyinfraformat",
    version="0.1.0a-dev",
    description="Python library for Finnish Infraformat",
    long_description=long_description,
    author="Ari Hartikainen & Taavi Dettenborn & Martti Hallipelto",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="infraformat",
    packages=find_packages(exclude=["docs", "tests"]),
    install_requires=["numpy", "pandas"],
)
