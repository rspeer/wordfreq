from wordfreq.build import load_all_data
from wordfreq.transfer import download_and_extract_raw_data
from wordfreq import config
import os
import tempfile
import shutil


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

        assert open(db_file).read() == open(config.DB_FILENAME).read()
    finally:
        shutil.rmtree(tempdir)
