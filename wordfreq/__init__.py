from pkg_resources import resource_filename
from functools import lru_cache
import unicodedata
from ftfy import chardata
import langcodes
import itertools
import msgpack
import re
import gzip
import pathlib
import random
import logging
logger = logging.getLogger(__name__)

DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))

CACHE_SIZE = 100000

def _emoji_char_class():
    """
    Build a regex for emoji substitution.  First we create a regex character set
    (like "[a-cv-z]") matching characters we consider emoji (see the docstring
    of _replace_problem_text()).  The final regex matches one such character
    followed by any number of spaces and identical characters.
    """
    ranges = []
    for i, c in enumerate(chardata.CHAR_CLASS_STRING):
        if c == '3' and i >= 0x2600 and i != 0xfffd:
            if ranges and i == ranges[-1][1] + 1:
                ranges[-1][1] = i
            else:
                ranges.append([i, i])
    return '[%s]' % ''.join(chr(a) + '-' + chr(b) for a, b in ranges)

EMOJI_RANGE = _emoji_char_class()

def _non_punct_class():
    """
    Builds a regex that matches anything that is not a one of the following
    classes:
    - P: punctuation
    - S: symbols
    - Z: separators
    - M: combining marks
    - C: control characters
    This will classify symbols, including emoji, as punctuation; callers that
    want to treat emoji separately should filter them out first.
    """
    non_punct = DATA_PATH / 'non_punct.txt'
    try:
        with non_punct.open() as file:
            return file.read()
    except FileNotFoundError:
        non_punct = [x for x in range(0x110000)
                        if unicodedata.category(chr(x))[0] not in 'PSZMC']

        non_punct_ranges = to_ranges(non_punct)

        out = '[%s]' % ''.join("%s-%s" % (chr(start), chr(end))
                for start, end in non_punct_ranges)

        with non_punct.open(mode='w') as file:
            file.write(out)

        return out

def to_ranges(seq):
    """
    Converts a sequence of int's into a list of inclusives ranges
    """
    ranges = []
    start_range = seq[0]
    for previous, elem in zip(seq, seq[1:]):
        if elem - previous != 1:
            ranges.append((start_range, previous))
            start_range = elem
    ranges.append((start_range, seq[-1]))
    return ranges



NON_PUNCT_RANGE = _non_punct_class()

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
    return [token.lower() for token in TOKEN_RE.findall(text)]


def tokenize(text, lang):
    """
    Tokenize this text in a way that's straightforward but appropriate for
    the language.

    So far, this means that Japanese is handled by mecab_tokenize, and
    everything else is handled by simple_tokenize.

    Strings that are looked up in wordfreq will be run through this function
    first, so that they can be expected to match the data.
    """
    if lang == 'ja':
        from wordfreq.mecab import mecab_tokenize
        return mecab_tokenize(text)
    else:
        return simple_tokenize(text)


def read_cBpack(filename):
    """
    Read a file from an idiosyncratic format that we use for storing
    approximate word frequencies, called "cBpack".

    The cBpack format is as follows:

    - The file on disk is a gzipped file in msgpack format, which decodes to a
      list whose first element is a header, and whose remaining elements are
      lists of words, preceded by a header.

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
            "A frequency cannot be a positive number of decibels."
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
        for word in bucket:
            freqs[word] = cB_to_freq(-index)
    return freqs


def iter_wordlist(lang, wordlist='combined'):
    """
    Yield the words in a wordlist in approximate descending order of
    frequency.

    Because wordfreq rounds off its frequencies, the words will form 'bands'
    with the same rounded frequency, appearing in alphabetical order within
    each band.
    """
    for sublist in get_frequency_list(lang, wordlist):
        yield from sublist


def half_harmonic_mean(a, b):
    """
    An associative, commutative, monotonic function that returns a value
    less than or equal to both a and b.

    Used for estimating the frequency of terms made of multiple tokens, given
    the assumption that the tokens very frequently appear together.
    """
    return (a * b) / (a + b)


@lru_cache(maxsize=CACHE_SIZE)
def word_frequency(word, lang, wordlist='combined', default=0.):
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`. The default (and currently only) wordlist is
    'combined', built from whichever of these four sources have sufficient
    data for the language:

      - Full text of Wikipedia
      - A sample of 72 million tweets collected from Twitter in 2014,
        divided roughly into languages using automatic language detection
      - Frequencies extracted from OpenSubtitles
      - The Leeds Internet Corpus

    Words that we believe occur at least once per million tokens, based on
    the average of these lists, will appear in the word frequency list.
    If you look up a word that's not in the list, you'll get the `default`
    value, which itself defaults to 0.

    If a word decomposes into multiple tokens, we'll return a smoothed estimate
    of the word frequency that is no greater than the frequency of any of its
    individual tokens.
    """
    freqs = get_frequency_dict(lang, wordlist)
    combined_value = None
    tokens = tokenize(word, lang)

    if len(tokens) == 0:
        return default

    for token in tokens:
        if token not in freqs:
            # If any word is missing, just return the default value
            return default
        value = freqs[token]
        if combined_value is None:
            combined_value = value
        else:
            # Combine word values using the half-harmonic-mean formula,
            # (a * b) / (a + b). This operation is associative.
            combined_value = half_harmonic_mean(combined_value, value)
    return combined_value


@lru_cache(maxsize=100)
def top_n_list(lang, n, wordlist='combined', ascii_only=False):
    results = []
    for word in iter_wordlist(lang, wordlist):
        if (not ascii_only) or max(word) <= '~':
            results.append(word)
            if len(results) >= n:
                break
    return results


def random_words(lang='en', wordlist='combined', nwords=4, bits_per_word=12,
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
    selected = [random.choice(choices) for i in range(nwords)]
    return ' '.join(selected)


def random_ascii_words(lang='en', wordlist='combined', nwords=4,
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
