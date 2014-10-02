from wordfreq.config import DB_FILENAME, CACHE_SIZE
from wordfreq.util import standardize_word
import sqlite3
import sys

if sys.version_info.major == 2:
    from functools32 import lru_cache
    PY2 = True
else:
    from functools import lru_cache
    PY2 = False

SQLITE_ERROR_TEXT = """
Couldn't open the wordlist database.
You may need to run wordfreq's setup.py script.

I was expecting to find the database at:

    %(path)s

This can be configured by setting the WORDFREQ_DATA environment variable.
""" % {'path': DB_FILENAME}

try:
    if PY2:
        CONN = sqlite3.connect(DB_FILENAME)
    else:
        CONN = sqlite3.connect(DB_FILENAME, check_same_thread=False)
except sqlite3.OperationalError:
    raise IOError(SQLITE_ERROR_TEXT)


@lru_cache(maxsize=CACHE_SIZE)
def word_frequency(word, lang, wordlist='multi', offset=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`.

    The offset gets added to all values, to monotonically account for the
    fact that we have not observed all possible words.
    """
    c = CONN.cursor()
    c.execute("SELECT freq from words where word=? and lang=? and wordlist=?",
              (standardize_word(word), lang, wordlist))
    row = c.fetchone()
    if row is None:
        return offset
    else:
        return row[0] + offset


def wordlist_size(wordlist, lang=None):
    """
    Get the number of words in a wordlist.
    """
    c = CONN.cursor()
    if lang is None:
        c.execute(
            "SELECT count(*) from words where wordlist=?",
            (wordlist,)
        )
    else:
        c.execute(
            "SELECT count(*) from words where wordlist=? and lang=?",
            (wordlist, lang)
        )
    return c.fetchone()[0]


def average_frequency(wordlist, lang):
    """
    A kind of slow function to get the average frequency for words in a
    wordlist.

    If, for example, you're smoothing over word frequencies by adding the
    same baseline number to all of them, this can tell you what a good
    baseline is. (For multi/en, it's 6.7e-07.)
    """
    c = CONN.cursor()
    c.execute("SELECT avg(freq) from words where wordlist=? and lang=?",
              (wordlist, lang))
    return c.fetchone()[0]


def iter_wordlist(wordlist='multi', lang=None):
    """
    Returns a generator, yielding (word, lang, frequency) triples from
    a wordlist in descending order of frequency.

    If a `lang` is specified, the results will only contain words in that
    language.
    """
    c = CONN.cursor()
    if lang is None:
        results = c.execute(
            "SELECT word, lang, freq from words where wordlist=? "
            "ORDER BY freq desc",
            (wordlist,)
        )
    else:
        results = c.execute(
            "SELECT word, lang, freq from words where "
            "wordlist=? and lang=? ORDER BY freq DESC",
            (wordlist, lang)
        )

    return results


def wordlist_info(connection=None):
    """
    Get info about all the wordlists in a database, returning their
    list name, language, and number of words as 'wordlist', 'lang',
    and 'count' respectively.

    The database connection can be given as an argument, in order to get
    information about a database other than the default configured one.
    """
    if connection is None:
        connection = CONN
    c = connection.cursor()
    results = c.execute(
        "SELECT wordlist, lang, count(*) from words GROUP BY wordlist, lang"
    )
    for wordlist, lang, count in results:
        yield {'wordlist': wordlist, 'lang': lang, 'count': count}


def random_words(nwords=4, bits_per_word=12, wordlist='google-books',
                 lang='en'):
    """
    There are a few reasons you might want to see a sample of words in a
    wordlist:

    - Generating test cases
    - Getting a feel for what a wordlist contains
    - Generating passwords as in https://xkcd.com/936/

    Parameters:

    - `nwords` is the number of words to select.
    - `bits_per_word` indicate how many bits of randomness per word you want,
      up to log2(wordlist_size). As you increase it, the words get obscure.
    - `wordlist` and `lang` specify the wordlist to use.
    """
    import random
    limit = 2 ** bits_per_word
    c = CONN.cursor()
    results = c.execute(
        "SELECT word from words where wordlist = ? and lang = ? "
        "ORDER BY freq DESC LIMIT ?",
        (wordlist, lang, limit)
    )
    words = [row[0] for row in results]
    selected = random.sample(words, nwords)
    return u' '.join(selected)
