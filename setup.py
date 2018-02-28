#!/usr/bin/env python
from setuptools import setup
import sys
import os

if sys.version_info[0] < 3:
    print("Sorry, but wordfreq no longer supports Python 2.")
    sys.exit(1)


classifiers = [
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development',
    'Topic :: Text Processing :: Linguistic',
]

current_dir = os.path.dirname(__file__)
README_contents = open(os.path.join(current_dir, 'README.md'),
                       encoding='utf-8').read()
doclines = README_contents.split("\n")
dependencies = [
    'ftfy >= 5', 'msgpack', 'langcodes >= 1.4', 'regex == 2017.07.28'
]
if sys.version_info < (3, 4):
    dependencies.append('pathlib')


setup(
    name="wordfreq",
    version='1.7.0',
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='info@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq/',
    license = "MIT",
    platforms = ["any"],
    description = doclines[0],
    classifiers = classifiers,
    long_description = "\n".join(doclines[2:]),
    packages=['wordfreq'],
    include_package_data=True,
    install_requires=dependencies,

    # mecab-python3 is required for looking up Japanese or Korean word
    # frequencies. In turn, it depends on libmecab-dev being installed on the
    # system. It's not listed under 'install_requires' because wordfreq should
    # be usable in other languages without it.
    #
    # Similarly, jieba is required for Chinese word frequencies.
    extras_require={
        'mecab': 'mecab-python3',
        'jieba': 'jieba'
    },
    tests_require=['mecab-python3', 'jieba'],
)
