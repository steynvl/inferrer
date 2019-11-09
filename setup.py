#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="inferrer",
    description="An automata learning library written in Python.",
    version="0.1.0",
    author="Steyn van Litsenborgh",
    url="https://github.com/steynvl/inferrer",
    long_description=Path("README.md").read_text(),
    long_description_content_type='text/markdown',
    keywords='automata-learning, python',
    packages=find_packages(include="inferrer*"),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=["graphviz"],
    tests_require=["pytest"],
    python_requires='>=3.7',
)
