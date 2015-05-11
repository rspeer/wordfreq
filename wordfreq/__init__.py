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


def tokenize(text):
    """
    A simple tokenizer that can be applied to most languages. Strings that
    are looked up in wordfreq will be run through this tokenizer first,
    so that they can be expected to match the data.
    """
    return [token.lower() for token in TOKEN_RE.findall(text)]


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
        got = msgpack.load(infile, encoding='utf-8')
    return got


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
            available[lang] = path
    return available


@lru_cache(maxsize=None)
def get_frequency_list(lang, wordlist='combined', match_cutoff=50):
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

    # Convert the LanguageData object to a normalized language code
    got = str(best)
    if got != lang:
        logger.warning(
            "You asked for word frequencies in language %r. Using the "
            "nearest match, which is %r (%s)."
            % (lang, best.language_name('en'))
        )

    filepath = available[str(best)]
    return read_dBpack(str(filepath))


def dB_to_freq(dB):
    if dB > 0:
        raise ValueError(
            "A frequency cannot be a positive number of decibels."
        )
    return 10 ** (dB / 10)


@lru_cache(maxsize=None)
def get_frequency_dict(lang, wordlist='combined', match_cutoff=50):
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
        for word in sublist:
            yield word


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
    for token in tokenize(word):
        if token not in freqs:
            # If any word is missing, just return the default value
            return default
        value = freqs[token]
        if combined_value is None:
            combined_value = value
        else:
            # Combine word values using the half-harmonic-mean formula,
            # (a * b) / (a + b). This operation is associative.
            combined_value = (combined_value * value) / (combined_value + value)
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


def random_words(nwords=4, lang='en', wordlist='combined', bits_per_word=12,
                 ascii_only=False):
    n_choices = 2 ** bits_per_word
    choices = top_n_list(lang, n_choices, wordlist, ascii_only=ascii_only)
    if len(choices) < n_choices:
        raise ValueError(
            "There aren't enough words in the wordlist to provide %d bits of "
            "entropy per word." % bits_per_word
        )
    selected = [random.choice(choices) for i in range(nwords)]
    return ' '.join(selected)


def random_ascii_words(nwords=4, lang='en', wordlist='combined',
                       bits_per_word=12):
    return random_words(nwords, lang, wordlist, bits_per_word, ascii_only=True)
