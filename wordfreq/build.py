from collections import defaultdict
import sqlite3
import codecs
import re
import os
import logging

from ftfy import ftfy
from wordfreq import config, schema

logger = logging.getLogger(__name__)


def read_csv(filename):
    """
    Load word frequencies from a file of comma-separated values, where
    each line contains a term, a comma, and its frequency.

    Scale the frequencies so they add up to 1.0, and return them as a
    dictionary.
    """
    return _scale_freqs(_read_csv_basic(filename))


def read_multilingual_csv(filename):
    """
    Load word frequencies from a file of comma-separated values, where
    each line is of the form:

        term|lang,freq

    Scale the frequencies so they add up to 1.0 *for each language*,
    and return a dictionary from language -> (word -> freq).
    """
    unscaled = defaultdict(dict)
    raw_freqs = _read_csv_basic(filename)
    for termlang in raw_freqs:
        term, lang = termlang.rsplit('|', 1)
        unscaled[lang][term] = raw_freqs[termlang]

    scaled = {}
    for key in unscaled:
        scaled[key] = _scale_freqs(unscaled[key])
    return scaled


def _read_csv_basic(filename):
    infile = codecs.open(filename, encoding='utf-8')

    counts = {}
    for line in infile:
        line = line.rstrip(u'\n')
        word, count = line.rsplit(u',', 1)
        count = float(count)
        counts[word] = count
    return counts


NUMBER_RE = re.compile(u'[0-9]+')
def read_leeds_corpus(filename):
    """
    Load word frequencies from a "Web as Corpus" file, collected and
    provided by the University of Leeds.

    For more information, see: http://corpus.leeds.ac.uk/list.html
    """
    infile = codecs.open(filename, encoding='utf-8')

    counts = defaultdict(float)
    for line in infile:
        line = line.rstrip()
        if line:
            rank = line.split(u' ')[0]
            if NUMBER_RE.match(rank) and line.count(u' ') == 2:
                _, freq, token = line.split(u' ')
                token = ftfy(token).lower()
                freq = float(freq)
                counts[token] += freq

    return _scale_freqs(counts)


def _scale_freqs(counts):
    """
    Take in unscaled word counts or frequencies, and scale them so that
    they add up to 1.0.
    """
    freqs = {}
    total = sum(counts.values())
    for word in counts:
        freqs[word] = counts[word] / total

    return freqs


def save_wordlist_to_db(conn, listname, lang, freqs):
    rows = [(listname, lang, word, freq)
            for word, freq in freqs.items()]
    conn.executemany(
        "INSERT OR REPLACE INTO words (wordlist, lang, word, freq) "
        "VALUES (?, ?, ?, ?)",
        rows
    )
    conn.commit()


def create_db(conn, filename):
    """
    Create a wordlist database, at the filename specified by `wordfreq.config`.

    This should be safe to run (and have no effect) if the database already
    exists.
    """
    base_dir = os.path.dirname(filename)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    conn.execute(schema.SCHEMA)
    for index_definition in schema.INDICES:
        conn.execute(index_definition)
    conn.commit()


LEEDS_LANGUAGES = ('ar', 'de', 'el', 'es', 'fr', 'it', 'ja', 'pt', 'ru', 'zh')
def load_all_data(source_dir=None, filename=None):
    """
    Load data from the raw data files into a SQLite database.
    """
    if source_dir is None:
        source_dir = config.RAW_DATA_DIR

    if filename is None:
        filename = config.DB_FILENAME

    conn = sqlite3.connect(filename)
    logger.info("Creating database")
    create_db(conn, filename)

    logger.info("Loading Leeds internet corpus:")
    for lang in LEEDS_LANGUAGES:
        logger.info("\tLanguage: %s" % lang)
        filename = os.path.join(
            source_dir, 'leeds', 'internet-%s-forms.num' % lang
        )
        wordlist = read_leeds_corpus(filename)
        save_wordlist_to_db(conn, 'leeds-internet', lang, wordlist)

    logger.info("Loading Google Books (English).")
    google_wordlist = read_csv(
        os.path.join(source_dir, 'google', 'google-books-english.csv')
    )
    save_wordlist_to_db(conn, 'google-books', 'en', google_wordlist)

    logger.info("Loading combined multilingual corpus:")
    multi_wordlist = read_multilingual_csv(
        os.path.join(source_dir, 'luminoso', 'multilingual.csv')
    )
    for lang in multi_wordlist:
        logger.info("\tLanguage: %s" % lang)
        save_wordlist_to_db(conn, 'multi', lang, multi_wordlist[lang])

    logger.info("Loading Twitter corpus.")
    twitter_wordlist = read_csv(
        os.path.join(source_dir, 'luminoso', 'twitter-52M.csv')
    )
    save_wordlist_to_db(conn, 'twitter', 'xx', twitter_wordlist)

    logger.info("Done loading.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_all_data()
