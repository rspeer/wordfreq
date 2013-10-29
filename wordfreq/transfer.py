import urllib, os, sys
import tarfile
from wordfreq import config
import logging
logger = logging.getLogger(__name__)


class ProgressTracker(object):
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


def download(url, dest_filename):
    """
    Download the file at `url` to `dest_filename`. Show a progress bar
    while downloading.
    """
    base_dir = os.path.dirname(dest_filename)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    tracker = ProgressTracker(url)
    urllib.urlretrieve(url, dest_filename, reporthook=tracker.report_progress)
    tracker.finish()
    logger.info("Saved database to %s" % dest_filename)
    return True


def download_and_extract_raw_data(url=None, root_dir=None):
    if url is None:
        url = config.RAW_DATA_URL

    if root_dir is None:
        root_dir = os.path.dirname(config.RAW_DATA_DIR)

    local_filename = os.path.join(root_dir, 'wordfreq-data.tar.gz')
    download(url, local_filename)

    logger.info("Extracting %s" % local_filename)
    with tarfile.open(local_filename, 'r') as tarf:
        tarf.extract_all(root_dir)


def download_db(url=None, target=None):
    if url is None:
        url = config.DB_URL

    if target is None:
        target = config.DB_FILENAME

    download(url, target)
