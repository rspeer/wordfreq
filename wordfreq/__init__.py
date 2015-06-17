from pkg_resources import resource_filename
from functools import lru_cache
import langcodes
import msgpack
import re
import gzip
import pathlib
import random
import logging
logger = logging.getLogger(__name__)


NON_PUNCT_RANGE = '[0-9A-Za-zª²³¹º\xc0-\u1fff\u2070-\u2fff\u301f-\ufeff０-９Ａ-Ｚａ-ｚ\uff66-\U0002ffff]'
NON_PUNCT_RE = re.compile(NON_PUNCT_RANGE)
TOKEN_RE = re.compile("{0}+(?:'{0}+)*".format(NON_PUNCT_RANGE))
DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))

CACHE_SIZE = 100000


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


def read_dBpack(filename):
    """
    Read a file from an idiosyncratic format that we use for storing
    approximate word frequencies, called "dBpack".

    The dBpack format is as follows:

    - The file on disk is a gzipped file in msgpack format, which decodes to a
      list of lists of words.

    - Each inner list of words corresponds to a particular word frequency,
      rounded to the nearest decibel. 0 dB represents a word that occurs with
      probability 1, so it is the only word in the data (this of course doesn't
      happen). -20 dB represents a word that occurs once per 100 tokens, -30 dB
      represents a word that occurs once per 1000 tokens, and so on.

    - The index of each list within the overall list is the negative of its
      frequency in decibels.

    - Each inner list is sorted in alphabetical order.

    As an example, consider a corpus consisting only of the words "red fish
    blue fish". The word "fish" occurs as 50% of tokens (-3 dB), while "red"
    and "blue" occur as 25% of tokens (-6 dB). The dBpack file of their word
    frequencies would decode to this list:

        [[], [], [], ['fish'], [], [], ['blue', 'red']]
    """
    with gzip.open(filename, 'rb') as infile:
        return msgpack.load(infile, encoding='utf-8')


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
    lists. (See `read_dBpack` for what this represents.)

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

    return read_dBpack(available[best])


def dB_to_freq(dB):
    """
    Decibels are a logarithmic scale of frequency. 0dB represents a frequency
    of 1 (it happens every time). -10dB represents a frequency of 1/10, or
    1 in every 10. -20dB represents a frequency of 1/100. In general x dB
    represents a frequency of 10 ** (x/10)
    """
    if dB > 0:
        raise ValueError(
            "A frequency cannot be a positive number of decibels."
        )
    return 10 ** (dB / 10)


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
            freqs[word] = dB_to_freq(-index)
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
    for token in tokenize(word, lang):
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

    These words are are of the given language and from the given wordlist.
    There are a total of nwords words in the string.
    bits_per_word is an estimate of the entropy provided by each word.
    You can restrict the selection of words to those written in ASCII
    characters by setting ascii_only to True.
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
    Returns a string of random, space separated, ascii words.

    These words are are of the given language and from the given wordlist.
    There are a total of nwords words in the string.
    bits_per_word is an estimate of the entropy provided by each word.
    """
    return random_words(lang, wordlist, nwords, bits_per_word, ascii_only=True)
