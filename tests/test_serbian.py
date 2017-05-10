from nose.tools import eq_
from wordfreq import tokenize


def test_transliteration():
    # "Well, there's a lot of things you do not understand."
    # (from somewhere in OpenSubtitles)
    eq_(tokenize("Па, има ту много ствари које не схваташ.", 'sr'),
        ['pa', 'ima', 'tu', 'mnogo', 'stvari', 'koje', 'ne', 'shvataš'])
    eq_(tokenize("Pa, ima tu mnogo stvari koje ne shvataš.", 'sr'),
        ['pa', 'ima', 'tu', 'mnogo', 'stvari', 'koje', 'ne', 'shvataš'])


def test_actually_russian():
    # This looks mostly like Serbian, but was probably actually Russian.
    # In Russian, Google Translate says it means:
    # "a hundred out of a hundred, boys!"
    #
    # We make sure to handle this case so we don't end up with a mixed-script
    # word like "pacanы".

    eq_(tokenize("сто из ста, пацаны!", 'sr'),
        ['sto', 'iz', 'sta', 'pacany'])

    eq_(tokenize("культуры", 'sr'), ["kul'tury"])


def test_alternate_codes():
    # Try language codes for Serbo-Croatian that have been split, and now
    # are canonically mapped to Serbian
    eq_(tokenize("культуры", 'sh'), ["kul'tury"])
    eq_(tokenize("культуры", 'hbs'), ["kul'tury"])

