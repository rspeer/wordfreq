from pkg_resources import resource_filename
from functools import lru_cache
from typing import List, Dict, Iterator, Tuple
import langcodes
import msgpack
import gzip
import itertools
import pathlib
import random
import logging
import math
import warnings

from .tokens import tokenize, simple_tokenize, lossy_tokenize
from .language_info import get_language_info
from .numbers import digit_freq, has_digit_sequence, smash_numbers

logger = logging.getLogger(__name__)


CACHE_SIZE = 100000
DATA_PATH = pathlib.Path(resource_filename("wordfreq", "data"))

# We'll divide the frequency by 10 for each token boundary that was inferred.
# (We determined the factor of 10 empirically by looking at words in the
# Chinese wordlist that weren't common enough to be identified by the
# tokenizer. These words would get split into multiple tokens, and their
# inferred frequency would be on average 9.77 times higher than their actual
# frequency.)
INFERRED_SPACE_FACTOR = 10.0

# tokenize and simple_tokenize are imported so that other things can import
# them from here. Suppress the pyflakes warning.
tokenize = tokenize
simple_tokenize = simple_tokenize


def read_cBpack(filename: str) -> List[List[str]]:
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
    with gzip.open(filename, "rb") as infile:
        data = msgpack.load(infile, raw=False)
    header = data[0]
    if (
        not isinstance(header, dict)
        or header.get("format") != "cB"
        or header.get("version") != 1
    ):
        raise ValueError("Unexpected header: %r" % header)
    return data[1:]


def available_languages(wordlist: str = "best") -> Dict[str, str]:
    """
    Given a wordlist name, return a dictionary of language codes to filenames,
    representing all the languages in which that wordlist is available.
    """
    if wordlist == "best":
        available = available_languages("small")
        available.update(available_languages("large"))
        return available
    elif wordlist == "combined":
        logger.warning("The 'combined' wordlists have been renamed to 'small'.")
        wordlist = "small"

    available = {}
    for path in DATA_PATH.glob("*.msgpack.gz"):
        if not path.name.startswith("_"):
            list_name = path.name.split(".")[0]
            name, lang = list_name.split("_")
            if name == wordlist:
                available[lang] = str(path)
    return available


@lru_cache(maxsize=None)
def get_frequency_list(
    lang: str, wordlist: str = "best", match_cutoff: None = None
) -> List[List[str]]:
    """
    Read the raw data from a wordlist file, returning it as a list of
    lists. (See `read_cBpack` for what this represents.)

    Because we use the `langcodes` module, we can handle slight
    variations in language codes. For example, looking for 'pt-BR',
    'pt_br', or even 'PT_BR' will get you the 'pt' (Portuguese) list.
    Looking up the alternate code 'por' will also get the same list.
    """
    if match_cutoff is not None:
        warnings.warn("The `match_cutoff` parameter is deprecated", DeprecationWarning)
    available = available_languages(wordlist)

    # the max_distance is high because we unify scripts, such as Traditional
    # vs. Simplified Chinese, in one wordlist
    best, _distance = langcodes.closest_match(lang, list(available), max_distance=60)
    if best == "und":
        raise LookupError("No wordlist %r available for language %r" % (wordlist, lang))

    if best != lang:
        logger.warning(
            "You asked for word frequencies in language %r. Using the "
            "nearest match, which is %r." % (lang, best)
        )

    return read_cBpack(available[best])


def cB_to_freq(cB: int) -> float:
    """
    Convert a word frequency from the logarithmic centibel scale that we use
    internally, to a proportion from 0 to 1.

    On this scale, 0 cB represents the maximum possible frequency of
    1.0. -100 cB represents a word that happens 1 in 10 times,
    -200 cB represents something that happens 1 in 100 times, and so on.

    In general, x cB represents a frequency of 10 ** (x/100).
    """
    if cB > 0:
        raise ValueError("A frequency cannot be a positive number of centibels.")
    return 10 ** (cB / 100)


def cB_to_zipf(cB: int) -> float:
    """
    Convert a word frequency from centibels to the Zipf scale
    (see `zipf_to_freq`).

    The Zipf scale is related to centibels, the logarithmic unit that wordfreq
    uses internally, because the Zipf unit is simply the bel, with a different
    zero point. To convert centibels to Zipf, add 900 and divide by 100.
    """
    return (cB + 900) / 100


def zipf_to_freq(zipf: float) -> float:
    """
    Convert a word frequency from the Zipf scale to a proportion between 0 and
    1.

    The Zipf scale is a logarithmic frequency scale proposed by Marc Brysbaert,
    who compiled the SUBTLEX data. The goal of the Zipf scale is to map
    reasonable word frequencies to understandable, small positive numbers.

    A word rates as x on the Zipf scale when it occurs 10**x times per billion
    words. For example, a word that occurs once per million words is at 3.0 on
    the Zipf scale.
    """
    return 10**zipf / 1e9


def freq_to_zipf(freq: float) -> float:
    """
    Convert a word frequency from a proportion between 0 and 1 to the
    Zipf scale (see `zipf_to_freq`).
    """
    return math.log(freq, 10) + 9


@lru_cache(maxsize=None)
def get_frequency_dict(
    lang: str, wordlist: str = "best", match_cutoff: None = None
) -> Dict[str, float]:
    """
    Get a word frequency list as a dictionary, mapping tokens to
    frequencies as floating-point probabilities.
    """
    if match_cutoff is not None:
        warnings.warn("The `match_cutoff` parameter is deprecated", DeprecationWarning)
    freqs = {}
    pack = get_frequency_list(lang, wordlist)
    for index, bucket in enumerate(pack):
        freq = cB_to_freq(-index)
        for word in bucket:
            freqs[word] = freq
    return freqs


def iter_wordlist(lang: str, wordlist: str = "best") -> Iterator[str]:
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
_wf_cache: Dict[Tuple[str, str, str, float], float] = {}


def _word_frequency(word: str, lang: str, wordlist: str, minimum: float) -> float:
    tokens = lossy_tokenize(word, lang)

    if not tokens:
        return minimum

    # Frequencies for multiple tokens are combined using the formula
    #     1 / f = 1 / f1 + 1 / f2 + ...
    # Thus the resulting frequency is less than any individual frequency, and
    # the smallest frequency dominates the sum.
    freqs = get_frequency_dict(lang, wordlist)
    one_over_result = 0.0
    for token in tokens:
        smashed = smash_numbers(token)
        if smashed not in freqs:
            # If any word is missing, just return the default value
            return minimum
        freq = freqs[smashed]
        if smashed != token:
            # If there is a digit sequence in the token, the digits are
            # internally replaced by 0s to aggregate their probabilities
            # together. We then assign a specific frequency to the digit
            # sequence using the `digit_freq` distribution.
            freq *= digit_freq(token)
        one_over_result += 1.0 / freq

    # Combine the frequencies of tokens we looked up.
    freq = 1.0 / one_over_result

    if get_language_info(lang)["tokenizer"] == "jieba":
        # If we used the Jieba tokenizer, we could tokenize anything to match
        # our wordlist, even nonsense. To counteract this, we multiply by a
        # probability for each word break that was inferred.
        freq *= INFERRED_SPACE_FACTOR ** -(len(tokens) - 1)

    # All our frequency data is only precise to within 1% anyway, so round
    # it to 3 significant digits
    unrounded = max(freq, minimum)
    if unrounded == 0.0:
        return 0.0
    else:
        leading_zeroes = math.floor(-math.log(unrounded, 10))
        return round(unrounded, leading_zeroes + 3)


def word_frequency(
    word: str, lang: str, wordlist: str = "best", minimum: float = 0.0
) -> float:
    """
    Get the frequency of `word` in the language with code `lang`, from the
    specified `wordlist`.

    These wordlists can be specified:

    - 'large': a wordlist built from at least 5 sources, containing word
      frequencies of 10^-8 and higher
    - 'small': a wordlist built from at least 3 sources, containing word
      frquencies of 10^-6 and higher
    - 'best': uses 'large' if available, and 'small' otherwise

    The value returned will always be at least as large as `minimum`.
    You could set this value to 10^-8, for example, to return 10^-8 for
    unknown words in the 'large' list instead of 0, avoiding a discontinuity.
    """
    args = (word, lang, wordlist, minimum)
    try:
        return _wf_cache[args]
    except KeyError:
        if len(_wf_cache) >= CACHE_SIZE:
            _wf_cache.clear()
        _wf_cache[args] = _word_frequency(*args)
        return _wf_cache[args]


def zipf_frequency(word: str, lang: str, wordlist: str = "best", minimum: float = 0.0):
    """
    Get the frequency of `word`, in the language with code `lang`, on the Zipf
    scale.

    The Zipf scale is a logarithmic frequency scale proposed by Marc Brysbaert,
    who compiled the SUBTLEX data. The goal of the Zipf scale is to map
    reasonable word frequencies to understandable, small positive numbers.

    A word rates as x on the Zipf scale when it occurs 10**x times per billion
    words. For example, a word that occurs once per million words is at 3.0 on
    the Zipf scale.

    Zipf values for reasonable words are between 0 and 8. The value this
    function returns will always be at last as large as `minimum`, even for a
    word that never appears. The default minimum is 0, representing words
    that appear once per billion words or less.

    wordfreq internally quantizes its frequencies to centibels, which are
    1/100 of a Zipf unit. The output of `zipf_frequency` will be rounded to
    the nearest hundredth to match this quantization.
    """
    freq_min = zipf_to_freq(minimum)
    freq = word_frequency(word, lang, wordlist, freq_min)
    return round(freq_to_zipf(freq), 2)


@lru_cache(maxsize=100)
def top_n_list(
    lang: str, n: int, wordlist: str = "best", ascii_only: bool = False
) -> List[str]:
    """
    Return a frequency list of length `n` in descending order of frequency.
    This list contains words from `wordlist`, of the given language.
    If `ascii_only`, then only ascii words are considered.

    The frequency list will not contain multi-digit sequences, because we
    estimate the frequencies of those using the functions in `numbers.py`,
    not using a wordlist that contains all of them.
    """
    results = []
    for word in iter_wordlist(lang, wordlist):
        if (not ascii_only) or max(word) <= "~":
            if not has_digit_sequence(word):
                results.append(word)
                if len(results) >= n:
                    break
    return results


def random_words(
    lang: str = "en",
    wordlist: str = "best",
    nwords: int = 5,
    bits_per_word: int = 12,
    ascii_only: bool = False,
) -> str:
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
    n_choices = 2**bits_per_word
    choices = top_n_list(lang, n_choices, wordlist, ascii_only=ascii_only)
    if len(choices) < n_choices:
        raise ValueError(
            "There aren't enough words in the wordlist to provide %d bits of "
            "entropy per word." % bits_per_word
        )
    return " ".join([random.choice(choices) for i in range(nwords)])


def random_ascii_words(
    lang: str = "en", wordlist: str = "best", nwords: int = 5, bits_per_word: int = 12
) -> str:
    """
    Returns a string of random, space separated, ASCII words.

    These words are of the given language and from the given wordlist.
    There will be `nwords` words in the string.

    `bits_per_word` determines the amount of entropy provided by each word;
    when it's higher, this function will choose from a larger list of
    words, some of which are more rare.
    """
    return random_words(lang, wordlist, nwords, bits_per_word, ascii_only=True)
