# Make wordfreq.query available at the top level when needed.

def word_frequency(word, lang, wordlist='multi', offset=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`.

    The offset gets added to all values, to monotonically account for the
    fact that we have not observed all possible words.

    This is a wrapper for the real word_frequency function, so that it can
    be imported at the top level instead of from `wordfreq.query`.
    """
    from wordfreq.query import word_frequency as _real_word_frequency
    return _real_word_frequency(word, lang, wordlist=wordlist, offset=offset)

