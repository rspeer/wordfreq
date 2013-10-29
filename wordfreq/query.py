from wordfreq.config import DB_FILENAME, CACHE_SIZE
from functools32 import lru_cache
import sqlite3

SQLITE_ERROR_TEXT = """
Couldn't open the wordlist database.
You may need to run wordfreq's setup.py script.

I was expecting to find the database at:

    %(path)s

This can be configured by setting the WORDFREQ_DATA environment variable.
""" % {'path': DB_FILENAME}

try:
    CONN = sqlite3.connect(DB_FILENAME)
except sqlite3.OperationalError:
    raise IOError(SQLITE_ERROR_TEXT)


@lru_cache(maxsize=CACHE_SIZE)
def word_frequency(word, lang, wordlist='multi', default=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`.

    If the word doesn't appear in the wordlist, return the default value.
    """
    c = CONN.cursor()
    c.execute("SELECT freq from words where word=? and lang=? and wordlist=?",
              (word, lang, wordlist))
    row = c.fetchone()
    if row is None:
        return default
    else:
        return row[0]


def iter_wordlist(wordlist, lang=None):
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


METANL_CONSTANT = 50291582140.06433
def metanl_word_frequency(word, lang, default=0.):
    """
    Return a word's frequency in a form that matches the output of
    metanl 0.6.
    
    In wordfreq, frequencies are proportions. They add up to 1 within a
    wordlist and language.

    In metanl, we had decided arbitrarily that common words should have a
    frequency of a billion or so. There was no real reason.

    This function provides compatibility by adapting wordfreq to give the
    same output as metanl. It does this by multiplying the word frequency in
    the 'multi' list by a big ugly constant. Oh well.
    """
    freq = word_frequency(word, lang, 'multi', default=None)
    if freq is None:
        return default
    else:
        return freq * METANL_CONSTANT
