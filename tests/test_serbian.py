from nose.tools import eq_
from wordfreq import tokenize


def test_transliteration():
    # "Well, there's a lot of things you do not understand."
    # (from somewhere in OpenSubtitles)
    eq_(tokenize("Па, има ту много ствари које не схваташ.", 'sr'),
        ['pa', 'ima', 'tu', 'mnogo', 'stvari', 'koje', 'ne', 'shvataš'])
    eq_(tokenize("Pa, ima tu mnogo stvari koje ne shvataš.", 'sr'),
        ['pa', 'ima', 'tu', 'mnogo', 'stvari', 'koje', 'ne', 'shvataš'])

