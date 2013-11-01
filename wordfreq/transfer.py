"""
This module provides some functions that help us work with the
wordlist data files, so that they don't have to be stored in Git
or in the source package.

These functions won't be used in the course of using the wordfreq
package normally; instead, they're called from commands in setup.py.
"""

from wordfreq import config
import os
import sys
import shutil
import tempfile
import tarfile
import logging
import subprocess
logger = logging.getLogger(__name__)

if sys.version_info.major == 2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


class ProgressTracker(object):
    """
    This class watches the progress of a urllib download task, and updates
    sys.stdout when the percentage changes.
    """
    def __init__(self, url):
        self.url = url
        self.progress = None

    def report_progress(self, count, blockSize, totalSize):
        percent = int(count*blockSize*100/totalSize)
        if percent != self.progress:
            sys.stdout.write("\rDownloading %s... %2d%%" % (self.url, percent))
            sys.stdout.flush()
            self.progress = percent

    def finish(self):
        sys.stdout.write('\n')


def ensure_dir_exists(dest_filename):
    """
    Something we'll need to do often: given a filename we want to write to,
    make sure its containing directory exists.
    """
    base_dir = os.path.dirname(dest_filename)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)


def download(url, dest_filename):
    """
    Download the file at `url` to `dest_filename`. Show a progress bar
    while downloading.
    """
    ensure_dir_exists(dest_filename)
    tracker = ProgressTracker(url)
    urlretrieve(url, dest_filename, reporthook=tracker.report_progress)
    tracker.finish()
    logger.info("Saved database to %s", dest_filename)


def download_and_extract_raw_data(url=None, root_dir=None):
    """
    Download the .tar.gz of raw data that can be used to build the database.
    """
    if url is None:
        url = config.RAW_DATA_URL

    if root_dir is None:
        root_dir = os.path.dirname(config.RAW_DATA_DIR)

    dest_filename = os.path.join(root_dir, 'wordfreq-data.tar.gz')
    ensure_dir_exists(dest_filename)
    download(url, dest_filename)

    logger.info("Extracting %s" % dest_filename)
    with tarfile.open(dest_filename, 'r') as tarf:
        tarf.extractall(root_dir)


def download_db(url=None, dest_filename=None):
    """
    Download the database itself, so we don't have to build it.
    """
    if url is None:
        url = config.DB_URL

    if dest_filename is None:
        dest_filename = config.DB_FILENAME

    ensure_dir_exists(dest_filename)
    download(url, dest_filename)


def upload_data(upload_path=None):
    """
    Collect the raw data and the database file, and upload them to an
    appropriate directory on the server that hosts downloads.

    This requires that it's running in a reasonable Unix environment,
    and more notably, that it has the proper SSH keys to upload to that
    server.
    """
    if upload_path is None:
        upload_path = config.UPLOAD_PATH
    
    build_dir = tempfile.mkdtemp('.wordfreq')
    version_dir = os.path.join(build_dir, config.MINOR_VERSION)
    os.makedirs(version_dir)

    source_filename = os.path.join(version_dir, 'wordfreq-data.tar.gz')
    logger.info("Creating %s" % source_filename)
    with tarfile.open(source_filename, 'w:gz') as tarf:
        tarf.add(config.RAW_DATA_DIR)

    logger.info("Copying database file %s" % config.DB_FILENAME)
    subprocess.call([
        '/bin/cp',
        config.DB_FILENAME,
        version_dir
    ])

    logger.info("Uploading to %s" % upload_path)
    subprocess.call([
        '/usr/bin/rsync',
        '-avz',
        version_dir,
        upload_path
    ])

    logger.info("Removing build directory %s" % build_dir)
    shutil.rmtree(build_dir)
