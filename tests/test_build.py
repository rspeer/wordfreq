from nose.tools import eq_
from wordfreq.build import load_all_data
from wordfreq.query import wordlist_info
from wordfreq.transfer import download_and_extract_raw_data
from wordfreq import config
import os
import tempfile
import shutil
import sqlite3


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
        eq_(flatten_list_of_dicts(wordlist_info(conn)),
            flatten_list_of_dicts(wordlist_info(None)))
    finally:
        shutil.rmtree(tempdir)
