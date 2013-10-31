#!/usr/bin/env python
from setuptools import setup
from distutils.core import Command
from setuptools.command.install import install
from setuptools.command.develop import develop

import os
import sys
import logging
logging.basicConfig(level=logging.INFO)

# Make sure we can import stuff from here.
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

from wordfreq import config, transfer

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


class SimpleCommand(Command):
    """
    Get the boilerplate out of the way for commands that take no options.
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class BuildDatabaseCommand(SimpleCommand):
    description = "Build the word frequency database from raw data"
    def run(self):
        from wordfreq.build import load_all_data
        load_all_data()


class DownloadDatabaseCommand(SimpleCommand):
    description = "Download the built word frequency database"
    user_options = []

    def run(self):
        transfer.download_db()


class DownloadRawDataCommand(SimpleCommand):
    description = "Download the raw wordlist data"
    user_options = []

    def run(self):
        transfer.download_and_extract_raw_data()


class UploadDataCommand(SimpleCommand):
    description = "Upload the raw data and database"
    user_options = []

    def run(self):
        transfer.upload_data()


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        if not os.path.exists(config.DB_FILENAME):
            self.run_command('download_db')


class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        if not os.path.exists(config.DB_FILENAME):
            self.run_command('download_db')


requirements = ['ftfy >= 3']
if sys.version_info.major == 2:
    requirements.append('functools32')

setup(
    name="wordfreq",
    version=config.VERSION,
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='dev@luminoso.com',
    url='http://github.com/LuminosoInsight/wordfreq/',
    license = "MIT",
    platforms = ["any"],
    description = doclines[0],
    classifiers = classifiers,
    long_description = "\n".join(doclines[2:]),
    packages=['wordfreq'],
    install_requires=requirements,
    cmdclass = {
        'build_db': BuildDatabaseCommand,
        'download_db': DownloadDatabaseCommand,
        'download_raw': DownloadRawDataCommand,
        'upload_data': UploadDataCommand,
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand
    }
)
