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
    'msgpack >= 1.0', 'langcodes >= 3.0', 'regex >= 2020.04.04'
]

setup(
    name="wordfreq",
    version='2.4.2',
    maintainer='Robyn Speer',
    maintainer_email='rspeer@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq/',
    license="MIT",
    platforms=["any"],
    description=doclines[0],
    classifiers=classifiers,
    long_description=README_contents,
    long_description_content_type='text/markdown',
    packages=['wordfreq'],
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=dependencies,

    # mecab-python3 is required for looking up Japanese or Korean word
    # frequencies. In turn, it depends on libmecab-dev being installed on the
    # system. It's not listed under 'install_requires' because wordfreq should
    # be usable in other languages without it.
    #
    # Similarly, jieba is required for Chinese word frequencies.
    extras_require={
        # previous names for extras
        'mecab': ['mecab-python3', 'ipadic', 'mecab-ko-dic'],
        'jieba': ['jieba >= 0.42'],

        # get them all at once
        'cjk': ['mecab-python3', 'ipadic', 'mecab-ko-dic', 'jieba >= 0.42']
    },
    tests_require=['pytest', 'mecab-python3', 'jieba >= 0.42', 'ipadic', 'mecab-ko-dic'],
)
