import os

DB_DIR = (os.environ.get('WORDFREQ_DATA')
          or os.path.expanduser('~/.cache/wordfreq'))
RAW_DATA_DIR = os.path.join(DB_DIR, 'raw_data')
VERSION = '0.1'
DB_FILENAME = os.path.join(DB_DIR, "words-%s.sqlite" % VERSION)
LRU_SIZE = 100000