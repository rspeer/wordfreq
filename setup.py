#!/usr/bin/env python
from setuptools import setup
from distutils.core import Command

# Make sure we can import stuff from here.
import os
import sys
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

from wordfreq.config import VERSION

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

README_contents = open(os.path.join(current_dir, 'README.txt')).read()
doclines = README_contents.split("\n")

setup(
    name="wordfreq",
    version=VERSION,
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='dev@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq/',
    license = "MIT",
    platforms = ["any"],
    description = doclines[0],
    classifiers = classifiers,
    long_description = "\n".join(doclines[2:]),
    packages=['wordfreq'],
    install_requires=['ftfy >= 3', 'functools32 == 3.2.3-1'],
)
