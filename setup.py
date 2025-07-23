"""Python setup information."""

import os
import re
from pathlib import Path

from setuptools import find_packages, setup

PROJECT_ROOT = Path(os.path.realpath(__file__)).parent
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
README_FILE = PROJECT_ROOT / "README.md"
VERSION_FILE = PROJECT_ROOT / "pyinfraformat" / "__init__.py"


def get_requirements():
    """Read contents from requirements.txt."""
    with open(REQUIREMENTS_FILE, encoding="utf-8") as buff:
        return buff.read().splitlines()


def get_long_description():
    """Read contents from README.md."""
    with open(README_FILE, encoding="utf-8") as buff:
        return buff.read()


def get_version():
    """Read version info from __init__.py."""
    with open(VERSION_FILE, encoding="utf-8") as buff:
        lines = buff.readlines()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in lines:
        version_search = re.search(version_regex, line, re.MULTILINE)
        if version_search:
            return version_search.group(1)
    raise RuntimeError("Unable to find version in %s." % (VERSION_FILE,))


setup(
    name="pyinfraformat",
    version=get_version(),
    description="Python library for Finnish Infraformat",
    author="Ari Hartikainen, Taavi Dettenborn, Martti Hallipelto",
    license="Apache-2.0",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="infraformat",
    packages=find_packages(exclude=["docs", "tests"]),
    package_data={"pyinfraformat": ["plots//icons//*.svg"]},
    install_requires=get_requirements(),
)
