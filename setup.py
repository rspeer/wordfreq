#!/usr/bin/env python

version_str = '0.1'

from setuptools import setup

classifiers=[
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: C',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development',
    'Topic :: Text Processing :: Linguistic',]

import os
README_contents = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
doclines = README_contents.split("\n")

setup(
    name="wordfreq",
    version=version_str,
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='dev@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq/',
    license = "MIT",
    platforms = ["any"],
    description = doclines[0],
    classifiers = classifiers,
    long_description = "\n".join(doclines[2:]),
    packages=['wordfreq'],
    package_data = {'wordfreq': ['data/wordlists/*.txt']},
    install_requires=['ftfy >= 3', 'functools32 == 3.2.3-1'],
)
