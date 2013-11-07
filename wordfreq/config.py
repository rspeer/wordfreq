import os

# This directory stores versions of the wordfreq database.
DB_DIR = (os.environ.get('WORDFREQ_DATA')
          or os.path.expanduser('~/.cache/wordfreq'))

# When the minor version number increments, the data may change.
VERSION = '0.3.0'
MINOR_VERSION = '.'.join(VERSION.split('.')[:2])

# Put these options together to make a database filename.
DB_FILENAME = os.path.join(DB_DIR, "wordfreq-%s.db" % MINOR_VERSION)

# How many words do we cache the frequencies for?
CACHE_SIZE = 100000

# Where can the data be downloaded from?
DOWNLOAD_URL = (os.environ.get('WORDFREQ_URL')
                or 'http://wordfreq.services.luminoso.com/')
RAW_DATA_URL = os.path.join(DOWNLOAD_URL, MINOR_VERSION, 'wordfreq-data.tar.gz')
DB_URL = os.path.join(DOWNLOAD_URL, MINOR_VERSION,
                      'wordfreq-%s.db' % MINOR_VERSION)

# How do we actually get it there? This is the path, including hostname, to give
# to scp to upload the file.
UPLOAD_PATH = 'baldr:/srv/wordfreq/static/'

# Where should raw data go? Inside the package isn't necessary a good
# place for it, because it might be installed in the system site-packages.
#
# The current directory -- as you're running the setup.py script -- seems
# as reasonable as anything.
RAW_DATA_DIR = './wordfreq_data'
