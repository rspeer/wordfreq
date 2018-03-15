from functools import lru_cache
from langcodes import Language, best_match


# Text in scripts written without spaces has to be handled specially in our
# tokenization regex (see TOKEN_RE in tokens.py). Also, when one of these is
# the script of the language we're analyzing, then we need to either have
# a specific tokenizer for the language or give up.
SPACELESS_SCRIPTS = [
    # Han ideographs are spaceless, but they don't need to appear in this list
    # because they have their own cases in get_language_info and TOKEN_RE.
    'Hiragana',
    # We omit katakana because Unicode regular expressions can already
    # tokenize sequences of katakana, and omitting it here means we can also
    # recognize a switch between hiragana and katakana as a token boundary.
    'Thai',  # Thai script
    'Khmr',  # Khmer script
    'Laoo',  # Lao script
    'Mymr',  # Burmese script
    'Tale',  # Tai Le script
    'Talu',  # Tai Lü script
    'Lana',  # Lanna script
]


def _language_in_list(language, targets, min_score=80):
    """
    A helper function to determine whether this language matches one of the
    target languages, with a match score above a certain threshold.

    The languages can be given as strings (language tags) or as Language
    objects. `targets` can be any iterable of such languages.
    """
    matched = best_match(language, targets, min_score=min_score)
    return matched[1] > 0


@lru_cache(maxsize=None)
def get_language_info(language):
    """
    Looks up the things we need to know about how to handle text in a given
    language. This will return a dictionary with the following fields:

    'script': a BCP 47 script code such as 'Latn', 'Cyrl', 'Hans'...

        Indicates the script that tokens in this language should be in,
        _after_ our preprocessing. The script for 'zh' is 'Hans', for example,
        because even if the input is in Traditional Chinese ('Hant'), we
        convert it to Simplified.

    'tokenizer': 'regex', 'jieba', 'mecab', or None

        Indicates the best way we know to separate tokens in the language.

        'regex' is what will be used for most languages, meaning that we can
        segment the text with a Unicode-aware regular expression. If a language
        generally uses spaces to separate words, the regex will work well.

        'jieba' and 'mecab' are tokenizers for specific languages written
        without spaces.

        A tokenizer of None means we don't have a good way to segment the
        language. We'll use the regex anyway, but the results will be pretty
        bad.

    'normal_form': 'NFC' or 'NFKC'

        How "should" Unicode be normalized when comparing text in this
        language? This is not a standard, it's just based on experience.
        Many languages need NFKC normalization for text comparisons to work
        properly, but in many European languages, NFKC normalization is
        excessive and loses information.

    'remove_marks': True or False

        Determines whether marks and decorations, such as vowel points and
        tatweels, should be removed. True for languages in abjad scripts.

    'dotless_i': True or False

        Is "ı" the lowercase of "I" in this language, as in Turkish?

    'diacritics_under': 'cedillas', 'commas', or None

        Should we convert any diacritics that are under the letters "s" and
        "t" in this language? 'cedillas' means we should convert commas to
        cedillas, and 'commas' means we should convert cedillas to commas.

    'transliteration': 'sr-Latn', 'az-Latn', or None

        Indicates a type of transliteration that we should use for normalizing
        a multi-script language. 'sr-Latn' means to use Serbian romanization,
        and 'az-Latn' means to use Azerbaijani romanization.

    'lookup_transliteration': 'zh-Hans' or None

        Indicates a lossy transliteration that should be not be used for output,
        but should be applied when looking up words in a list. 'zh-Hans' means
        that we should convert Traditional Chinese characters to Simplified.
    """
    # The input is probably a string, so parse it into a Language. If it's
    # already a Language, it will pass through.
    language = Language.get(language)

    # Assume additional things about the language, such as what script it's in,
    # using the "likely subtags" table
    language_full = language.maximize()

    # Start the `info` dictionary with default values, including the 'script'
    # value that we now know from `language_full`.
    info = {
        'script': language_full.script,
        'tokenizer': 'regex',
        'normal_form': 'NFKC',
        'remove_marks': False,
        'dotless_i': False,
        'diacritics_under': None,
        'transliteration': None,
        'lookup_transliteration': None
    }

    if _language_in_list(language, ['ja', 'ko']):
        info['tokenizer'] = 'mecab'
    elif _language_in_list(language, ['zh', 'yue']):
        info['tokenizer'] = 'jieba'
    elif info['script'] in SPACELESS_SCRIPTS:
        info['tokenizer'] = None

    # Cased alphabetic scripts get NFC normal form
    if info['script'] in ['Latn', 'Grek', 'Cyrl']:
        info['normal_form'] = 'NFC'

    if info['script'] in ['Arab', 'Hebr']:
        info['remove_marks'] = True

    if _language_in_list(language, ['tr', 'az', 'kk']):
        info['dotless_i'] = True
        info['diacritics_under'] = 'cedillas'
    elif _language_in_list(language, ['ro']):
        info['diacritics_under'] = 'commas'

    if _language_in_list(language, ['sr']):
        info['transliteration'] = 'sr-Latn'
    elif _language_in_list(language, ['az']):
        info['transliteration'] = 'az-Latn'

    if language.language == 'zh' and language.script != 'Hant':
        info['lookup_transliteration'] = 'zh-Hans'

    return info
