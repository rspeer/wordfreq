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
def word_frequency(word, lang, wordlist='multi', offset=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`.

    The offset gets added to all values, to monotonically account for the
    fact that we have not observed all possible words.
    """
    c = CONN.cursor()
    c.execute("SELECT freq from words where word=? and lang=? and wordlist=?",
              (word, lang, wordlist))
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


def get_wordlists():
    c = CONN.cursor()
    results = c.execute(
        "SELECT wordlist, lang, count(*) from words GROUP BY wordlist, lang"
    )
    for wordlist, lang, count in results:
        yield {'wordlist': wordlist, 'lang': lang, 'count': count}


METANL_CONSTANT = 50291582140.06433
def metanl_word_frequency(wordlang, offset=0.):
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
    word, lang = wordlang.rsplit('|', 1)
    freq = word_frequency(word, lang, 'multi',
                          offset = offset / METANL_CONSTANT)
    return freq * METANL_CONSTANT
