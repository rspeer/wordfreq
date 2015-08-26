from wordfreq_builder.word_counts import URL_RE
from nose.tools import eq_


def check_url(url):
    match = URL_RE.match(url)
    assert match
    eq_(match.span(), (0, len(url)))


def test_url_re():
    # URLs like this are all over the Arabic Wikipedia. Here's one with the
    # student ID blanked out.
    yield check_url, 'http://www.ju.edu.jo/alumnicard/0000000.aspx'

    yield check_url, 'https://example.com/űnicode.html'
    yield check_url, 'http://☃.net'

    assert not URL_RE.match('ftp://127.0.0.1')

