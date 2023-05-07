#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup

from _version import __version__

# Check that the Python version is supported
if sys.version_info < (3, 9) or sys.version_info >= (4,):
    raise RuntimeError("This package requires Python 3.9 or later")

# Package meta-data.
NAME = "CartPlayer"
PACKAGE = "cart_player"
DESCRIPTION = "Dump your GB(C) & GBA from your real cartridges, and backup / upload your saves."
URL = "https://github.com/djidane535/cart_player"
EMAIL = None
AUTHOR = "djidane535"
REQUIRES_PYTHON = ">=3.9, <4"

REQUIRED = [
    "Pillow==9.3.*",
    "PySimpleGUI==4.60.*",
    "easysettings==4.0.*",
    "pydantic==1.10.*",
    "rapidfuzz==2.13.*",
    "Unidecode==1.3.*",
    "requests==2.29.*",
    "pexpect==4.8.*;platform_system=='Darwin'",
    "appdirs==1.4.*;platform_system=='Darwin'",
]

EXTRA_REQUIRED = {
    "dev": ["flake8", "black", "pre-commit", "isort", "seed-isort-config"],
    "tests": ["pytest", "mock"],
}

setup(
    name=NAME,
    description=DESCRIPTION,
    version=__version__,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=[PACKAGE],
    python_requires=REQUIRES_PYTHON,
    install_requires=REQUIRED,
    extras_require=EXTRA_REQUIRED,
    include_package_data=True,
    zip_safe=False,
    license="GPLv2",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # Configure package versioning from source code management tool (i.e. git).
    use_scm_version={
        "local_scheme": lambda *_: "",  # do not prepend dirty-related tag to version
        "write_to": os.path.join("./", PACKAGE.replace(".", "/"), "_version.py"),
    },
    setup_requires=["setuptools_scm"],
)
