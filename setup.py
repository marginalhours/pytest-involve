#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-involve",
    version="0.1.4",
    author="Tom Keefe",
    author_email="tomlkeefe@gmail.com",
    maintainer="Tom Keefe",
    maintainer_email="tomlkeefe@gmail.com",
    license="MIT",
    url="https://github.com/MisterKeefe/pytest-involve",
    description="Run tests covering a specific file or changeset",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    py_modules=["pytest_involve"],
    python_requires=">=3.6",
    install_requires=["pytest>=3.5.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={"pytest11": ["involve = pytest_involve"]},
)
