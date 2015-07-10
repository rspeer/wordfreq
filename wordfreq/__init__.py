from pkg_resources import resource_filename
from functools import lru_cache
import langcodes
import msgpack
import re
import gzip
import itertools
import pathlib
import random
import logging
logger = logging.getLogger(__name__)


CACHE_SIZE = 100000
DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))

def load_range(filename):
    """
    Load a file from the data path.
    """
    with (DATA_PATH / filename).open() as file:
        return file.read()

EMOJI_RANGE = load_range('emoji.txt')
NON_PUNCT_RANGE = load_range('non_punct.txt')
COMBINING_MARK_RANGE = load_range('combining_mark.txt')

COMBINING_MARK_RE = re.compile(COMBINING_MARK_RANGE)
TOKEN_RE = re.compile("{0}|{1}+(?:'{1}+)*".format(EMOJI_RANGE, NON_PUNCT_RANGE))


def simple_tokenize(text):
    """
    A simple tokenizer that can be applied to most languages.

    It considers a word to be made of a sequence of 'token characters', an
    overly inclusive range that includes letters, Han characters, emoji, and a
    bunch of miscellaneous whatnot, but excludes most punctuation and
    whitespace.

    The single complication for the sake of English is that apostrophes are not
    considered part of the token if they appear on the edge of the character
    sequence, but they are if they appear internally. "cats'" is not a token,
    but "cat's" is.
    """
    return [token.casefold() for token in TOKEN_RE.findall(text)]


mecab_tokenize = None
def tokenize(text, lang):
    """
    Tokenize this text in a way that's straightforward but appropriate for
    the language.

    So far, this means that Japanese is handled by mecab_tokenize, and
    everything else is handled by simple_tokenize. Additionally, Arabic commas
    and combining marks are removed.

    Strings that are looked up in wordfreq will be run through this function
    first, so that they can be expected to match the data.
    """
    if lang == 'ja':
        global mecab_tokenize
        if mecab_tokenize is None:
            from wordfreq.mecab import mecab_tokenize
        return mecab_tokenize(text)

    if lang == 'ar':
        text = COMBINING_MARK_RE.sub('', text.replace('ـ', ''))

    return simple_tokenize(text)


def read_cBpack(filename):
    """
    Read a file from an idiosyncratic format that we use for storing
    approximate word frequencies, called "cBpack".

    The cBpack format is as follows:

    - The file on disk is a gzipped file in msgpack format, which decodes to a
      list whose first element is a header, and whose remaining elements are
      lists of words.

    - The header is a dictionary with 'format' and 'version' keys that make
      sure that we're reading the right thing.

    - Each inner list of words corresponds to a particular word frequency,
      rounded to the nearest centibel -- that is, one tenth of a decibel, or
      a factor of 10 ** .01.

      0 cB represents a word that occurs with probability 1, so it is the only
      word in the data (this of course doesn't happen). -200 cB represents a
      word that occurs once per 100 tokens, -300 cB represents a word that
      occurs once per 1000 tokens, and so on.

    - The index of each list within the overall list (without the header) is
      the negative of its frequency in centibels.

    - Each inner list is sorted in alphabetical order.

    As an example, consider a corpus consisting only of the words "red fish
    blue fish". The word "fish" occurs as 50% of tokens (-30 cB), while "red"
    and "blue" occur as 25% of tokens (-60 cB). The cBpack file of their word
    frequencies would decode to this:

        [
            {'format': 'cB', 'version': 1},
            [], [], [], ...    # 30 empty lists
            ['fish'],
            [], [], [], ...    # 29 more empty lists
            ['blue', 'red']
        ]
    """
    with gzip.open(filename, 'rb') as infile:
        data = msgpack.load(infile, encoding='utf-8')
    header = data[0]
    if (
        not isinstance(header, dict) or header.get('format') != 'cB'
        or header.get('version') != 1
    ):
        raise ValueError("Unexpected header: %r" % header)
    return data[1:]


def available_languages(wordlist='combined'):
    """
    List the languages (as language-code strings) that the wordlist of a given
    name is available in.
    """
    available = {}
    for path in DATA_PATH.glob('*.msgpack.gz'):
        list_name = path.name.split('.')[0]
        name, lang = list_name.split('_')
        if name == wordlist:
            available[lang] = str(path)
    return available


@lru_cache(maxsize=None)
def get_frequency_list(lang, wordlist='combined', match_cutoff=30):
    """
    Read the raw data from a wordlist file, returning it as a list of
    lists. (See `read_cBpack` for what this represents.)

    Because we use the `langcodes` module, we can handle slight
    variations in language codes. For example, looking for 'pt-BR',
    'pt_br', or even 'PT_BR' will get you the 'pt' (Portuguese) list.
    Looking up the alternate code 'por' will also get the same list.
    """
    available = available_languages(wordlist)
    best, score = langcodes.best_match(lang, list(available),
                                       min_score=match_cutoff)
    if score == 0:
        raise LookupError("No wordlist available for language %r" % lang)

    if best != lang:
        logger.warning(
            "You asked for word frequencies in language %r. Using the "
            "nearest match, which is %r (%s)."
            % (lang, best, langcodes.get(best).language_name('en'))
        )

    return read_cBpack(available[best])


def cB_to_freq(cB):
    """
    Convert a word frequency from the logarithmic centibel scale that we use
    internally, to a proportion from 0 to 1.

    On this scale, 0 cB represents the maximum possible frequency of
    1.0. -100 cB represents a word that happens 1 in 10 times,
    -200 cB represents something that happens 1 in 100 times, and so on.

    In general, x cB represents a frequency of 10 ** (x/100).
    """
    if cB > 0:
        raise ValueError(
            "A frequency cannot be a positive number of centibels."
        )
    return 10 ** (cB / 100)


@lru_cache(maxsize=None)
def get_frequency_dict(lang, wordlist='combined', match_cutoff=30):
    """
    Get a word frequency list as a dictionary, mapping tokens to
    frequencies as floating-point probabilities.
    """
    freqs = {}
    pack = get_frequency_list(lang, wordlist, match_cutoff)
    for index, bucket in enumerate(pack):
        freq = cB_to_freq(-index)
        for word in bucket:
            freqs[word] = freq
    return freqs


def iter_wordlist(lang, wordlist='combined'):
    """
    Yield the words in a wordlist in approximate descending order of
    frequency.

    Because wordfreq rounds off its frequencies, the words will form 'bands'
    with the same rounded frequency, appearing in alphabetical order within
    each band.
    """
    return itertools.chain(*get_frequency_list(lang, wordlist))


# This dict and inner function are used to implement a "drop everything" cache
# for word_frequency(); the overheads of lru_cache() are comparable to the time
# it takes to look up frequencies from scratch, so something faster is needed.
_wf_cache = {}

def _word_frequency(word, lang, wordlist, minimum):
    tokens = tokenize(word, lang)
    if not tokens:
        return minimum

    # Frequencies for multiple tokens are combined using the formula
    #     1 / f = 1 / f1 + 1 / f2 + ...
    # Thus the resulting frequency is less than any individual frequency, and
    # the smallest frequency dominates the sum.
    freqs = get_frequency_dict(lang, wordlist)
    one_over_result = 0.0
    for token in tokens:
        if token not in freqs:
            # If any word is missing, just return the default value
            return minimum
        one_over_result += 1.0 / freqs[token]

    return max(1.0 / one_over_result, minimum)

def word_frequency(word, lang, wordlist='combined', minimum=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`. The default wordlist is 'combined', built from
    whichever of these five sources have sufficient data for the language:

      - Full text of Wikipedia
      - A sample of 72 million tweets collected from Twitter in 2014,
        divided roughly into languages using automatic language detection
      - Frequencies extracted from OpenSubtitles
      - The Leeds Internet Corpus
      - Google Books Syntactic Ngrams 2013

    Another available wordlist is 'twitter', which uses only the data from
    Twitter.

    Words that we believe occur at least once per million tokens, based on
    the average of these lists, will appear in the word frequency list.

    The value returned will always be at least as large as `minimum`.

    If a word decomposes into multiple tokens, we'll return a smoothed estimate
    of the word frequency that is no greater than the frequency of any of its
    individual tokens.
    """
    args = (word, lang, wordlist, minimum)
    try:
        return _wf_cache[args]
    except KeyError:
        if len(_wf_cache) >= CACHE_SIZE:
            _wf_cache.clear()
        _wf_cache[args] = _word_frequency(*args)
        return _wf_cache[args]


@lru_cache(maxsize=100)
def top_n_list(lang, n, wordlist='combined', ascii_only=False):
    """
    Return a frequency list of length `n` in descending order of frequency.
    This list contains words from `wordlist`, of the given language.
    If `ascii_only`, then only ascii words are considered.
    """
    results = []
    for word in iter_wordlist(lang, wordlist):
        if (not ascii_only) or max(word) <= '~':
            results.append(word)
            if len(results) >= n:
                break
    return results


def random_words(lang='en', wordlist='combined', nwords=5, bits_per_word=12,
                 ascii_only=False):
    """
    Returns a string of random, space separated words.

    These words are of the given language and from the given wordlist.
    There will be `nwords` words in the string.

    `bits_per_word` determines the amount of entropy provided by each word;
    when it's higher, this function will choose from a larger list of
    words, some of which are more rare.

    You can restrict the selection of words to those written in ASCII
    characters by setting `ascii_only` to True.
    """
    n_choices = 2 ** bits_per_word
    choices = top_n_list(lang, n_choices, wordlist, ascii_only=ascii_only)
    if len(choices) < n_choices:
        raise ValueError(
            "There aren't enough words in the wordlist to provide %d bits of "
            "entropy per word." % bits_per_word
        )
    return ' '.join([random.choice(choices) for i in range(nwords)])


def random_ascii_words(lang='en', wordlist='combined', nwords=5,
                       bits_per_word=12):
    """
    Returns a string of random, space separated, ASCII words.

    These words are of the given language and from the given wordlist.
    There will be `nwords` words in the string.

    `bits_per_word` determines the amount of entropy provided by each word;
    when it's higher, this function will choose from a larger list of
    words, some of which are more rare.
    """
    return random_words(lang, wordlist, nwords, bits_per_word, ascii_only=True)
