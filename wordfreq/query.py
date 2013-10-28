from wordfreq.config import DB_FILENAME, LRU_SIZE
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


@lru_cache(maxsize=LRU_SIZE)
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

# I'm sorry.
METANL_CONSTANT = 50291582140.06433
def metanl_word_frequency(word, lang, default=0.):
    """
    Return a word's frequency in a form that matches the output of
    metanl 0.6.
    """
    freq = word_frequency(word, lang, 'multi', None)
    if freq is None:
        return default
    else:
        return freq * METANL_CONSTANT
