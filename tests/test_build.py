from nose.tools import eq_
from wordfreq.build import load_all_data
from wordfreq.query import wordlist_info
from wordfreq.transfer import download_and_extract_raw_data
from wordfreq import config
import os
import tempfile
import shutil
import sqlite3
import sys

PYTHON2 = (sys.version_info.major == 2)

def flatten_list_of_dicts(list_of_dicts):
    things = [sorted(d.items()) for d in list_of_dicts]
    return sorted(things)


def test_build():
    """
    Ensure that the build process builds the same DB that gets distributed.
    """
    if not os.path.exists(config.RAW_DATA_DIR):
        download_and_extract_raw_data()

    tempdir = tempfile.mkdtemp('.wordfreq')
    try:
        db_file = os.path.join(tempdir, 'test.db')
        load_all_data(config.RAW_DATA_DIR, db_file)
        conn = sqlite3.connect(db_file)

        # Compare the information we got to the information in the default DB.
        new_info = flatten_list_of_dicts(wordlist_info(conn))
        old_info = flatten_list_of_dicts(wordlist_info(None))
        eq_(len(new_info), len(old_info))
        for i in range(len(new_info)):
            # Don't test Greek and emoji on Python 2; we can't make them
            # consistent with Python 3.
            if PYTHON2 and ((u'lang', u'el') in new_info[i]):
                continue
            if PYTHON2 and ((u'wordlist', u'twitter') in new_info[i]):
                continue
            eq_(new_info[i], old_info[i])
    finally:
        shutil.rmtree(tempdir)
