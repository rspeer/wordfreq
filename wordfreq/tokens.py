import regex
import unicodedata
import logging
import langcodes

from .language_info import get_language_info, SPACELESS_SCRIPTS
from .preprocess import preprocess_text, smash_numbers

# Placeholders for CJK functions that we'll import on demand
_mecab_tokenize = None
_jieba_tokenize = None
_simplify_chinese = None

_WARNED_LANGUAGES = set()
logger = logging.getLogger(__name__)


def _make_spaceless_expr():
    scripts = sorted(SPACELESS_SCRIPTS)
    pieces = [r'\p{IsIdeo}'] + [r'\p{Script=%s}' % script_code for script_code in scripts]
    return ''.join(pieces)


SPACELESS_EXPR = _make_spaceless_expr()

TOKEN_RE = regex.compile(r"""
    # Case 1: a special case for non-spaced languages
    # -----------------------------------------------

    # Some scripts are written without spaces, and the Unicode algorithm
    # seems to overreact and insert word breaks between all their letters.
    # When we see sequences of characters in these scripts, we make sure not
    # to break them up. Such scripts include Han ideographs (\p{IsIdeo}),
    # hiragana (\p{Script=Hiragana}), and many Southeast Asian scripts such
    # as Thai and Khmer.
    #
    # Without this case, the standard rule (case 2) would make each character
    # a separate token. This would be the correct behavior for word-wrapping,
    # but a messy failure mode for NLP tokenization.
    #
    # If you have Chinese or Japanese text, it's certainly better to use a
    # tokenizer that's designed for it. Elsewhere in this file, we have
    # specific tokenizers that can handle Chinese and Japanese. With this
    # rule, though, at least this general tokenizer will fail less badly
    # on those languages.
    #
    # This rule is listed first so that it takes precedence. The placeholder
    # <SPACELESS> will be replaced by the complex range expression made by
    # _make_spaceless_expr().

    [<SPACELESS>]+ |

    # Case 2: standard Unicode segmentation
    # -------------------------------------

    # The start of the token must be 'word-like', not punctuation or whitespace
    # or various other things. However, we allow characters of category So
    # (Symbol - Other) because many of these are emoji, which can convey
    # meaning.

    (?=[\w\p{So}])

    # The start of the token must not be a letter followed by «'h». If it is,
    # we should use Case 3 to match up to the apostrophe, then match a new token
    # starting with «h». This rule lets us break «l'heure» into two tokens, just
    # like we would do for «l'arc».

    (?!\w'[Hh])

    # The entire token is made of graphemes (\X). Matching by graphemes means
    # that we don't have to specially account for marks or ZWJ sequences.
    #
    # The token ends as soon as it encounters a word break (\b). We use the
    # non-greedy match (+?) to make sure to end at the first word break we
    # encounter.
    \X+? \b |

    # If we were matching by codepoints (.) instead of graphemes (\X), then
    # detecting boundaries would be more difficult. Here's a fact that's subtle
    # and poorly documented: a position that's between codepoints, but in the
    # middle of a grapheme, does not match as a word break (\b), but also does
    # not match as not-a-word-break (\B). The word boundary algorithm simply
    # doesn't apply in such a position.
    #
    # We used to match the rest of the token using \S, which matches non-space
    # *codepoints*, and this caused us to incompletely work around cases where
    # it left off in the middle of a grapheme.
    #
    # Another subtle fact: the "non-breaking space" U+A0 counts as a word break
    # here. That's surprising, but it's also what we want, because we don't want
    # any kind of spaces in the middle of our tokens.

    # Case 3: Fix French
    # ------------------
    # This allows us to match the articles in French, Catalan, and related
    # languages, such as «l'», that we may have excluded from being part of
    # the token in Case 2.

    \w'
""".replace('<SPACELESS>', SPACELESS_EXPR), regex.V1 | regex.WORD | regex.VERBOSE)

TOKEN_RE_WITH_PUNCTUATION = regex.compile(r"""
    # This expression is similar to the expression above, but also matches any
    # sequence of punctuation characters.

    [<SPACELESS>]+ |
    [\p{punct}]+ |
    (?=[\w\p{So}]) (?!\w'[Hh]) \X+? \b |
    \w'
""".replace('<SPACELESS>', SPACELESS_EXPR), regex.V1 | regex.WORD | regex.VERBOSE)


# Just identify punctuation, for cases where the tokenizer is separate
PUNCT_RE = regex.compile(r"[\p{punct}]+")


def simple_tokenize(text, include_punctuation=False):
    """
    Tokenize the given text using a straightforward, Unicode-aware token
    expression.

    The expression mostly implements the rules of Unicode Annex #29 that
    are contained in the `regex` module's word boundary matching, including
    the refinement that splits words between apostrophes and vowels in order
    to separate tokens such as the French article «l'».

    It makes sure not to split in the middle of a grapheme, so that zero-width
    joiners and marks on Devanagari words work correctly.

    Our customizations to the expression are:

    - It leaves sequences of Chinese or Japanese characters (specifically, Han
      ideograms and hiragana) relatively untokenized, instead of splitting each
      character into its own token.

    - If `include_punctuation` is False (the default), it outputs only the
      tokens that start with a word-like character, or miscellaneous symbols
      such as emoji. If `include_punctuation` is True, it outputs all non-space
      tokens.

    - It keeps Southeast Asian scripts, such as Thai, glued together. This yields
      tokens that are much too long, but the alternative is that every grapheme
      would end up in its own token, which is worse.
    """
    text = unicodedata.normalize('NFC', text)
    if include_punctuation:
        return [
            token.casefold()
            for token in TOKEN_RE_WITH_PUNCTUATION.findall(text)
        ]
    else:
        return [
            token.strip("'").casefold()
            for token in TOKEN_RE.findall(text)
        ]


def tokenize(text, lang, include_punctuation=False, external_wordlist=False):
    """
    Tokenize this text in a way that's relatively simple but appropriate for
    the language. Strings that are looked up in wordfreq will be run through
    this function first, so that they can be expected to match the data.

    The text will be run through a number of pre-processing steps that vary
    by language; see the docstring of `wordfreq.preprocess.preprocess_text`.

    If `include_punctuation` is True, punctuation will be included as separate
    tokens. Otherwise, punctuation will be omitted in the output.

    CJK scripts
    -----------

    In the CJK languages, word boundaries can't usually be identified by a
    regular expression. Instead, there needs to be some language-specific
    handling. In Chinese, we use the Jieba tokenizer, with a custom word list
    to match the words whose frequencies we can look up. In Japanese and
    Korean, we use the MeCab tokenizer.

    The `external_wordlist` option only affects Chinese tokenization.  If it's
    True, then wordfreq will not use its own Chinese wordlist for tokenization.
    Instead, it will use the large wordlist packaged with the Jieba tokenizer,
    and it will leave Traditional Chinese characters as is. This will probably
    give more accurate tokenization, but the resulting tokens won't necessarily
    have word frequencies that can be looked up.

    If you end up seeing tokens that are entire phrases or sentences glued
    together, that probably means you passed in CJK text with the wrong
    language code.
    """
    # Use globals to load CJK tokenizers on demand, so that we can still run
    # in environments that lack the CJK dependencies
    global _mecab_tokenize, _jieba_tokenize

    language = langcodes.get(lang)
    info = get_language_info(language)
    text = preprocess_text(text, language)

    if info['tokenizer'] == 'mecab':
        from wordfreq.mecab import mecab_tokenize as _mecab_tokenize
        # Get just the language code out of the Language object, so we can
        # use it to select a MeCab dictionary
        tokens = _mecab_tokenize(text, language.language)
        if not include_punctuation:
            tokens = [token for token in tokens if not PUNCT_RE.match(token)]
    elif info['tokenizer'] == 'jieba':
        from wordfreq.chinese import jieba_tokenize as _jieba_tokenize
        tokens = _jieba_tokenize(text, external_wordlist=external_wordlist)
        if not include_punctuation:
            tokens = [token for token in tokens if not PUNCT_RE.match(token)]
    else:
        # This is the default case where we use the regex tokenizer. First
        # let's complain a bit if we ended up here because we don't have an
        # appropriate tokenizer.
        if info['tokenizer'] != 'regex' and lang not in _WARNED_LANGUAGES:
            logger.warning(
                "The language '{}' is in the '{}' script, which we don't "
                "have a tokenizer for. The results will be bad."
                .format(lang, info['script'])
            )
            _WARNED_LANGUAGES.add(lang)
        tokens = simple_tokenize(text, include_punctuation=include_punctuation)

    return tokens


def lossy_tokenize(text, lang, include_punctuation=False, external_wordlist=False):
    """
    Get a list of tokens for this text, with largely the same results and
    options as `tokenize`, but aggressively normalize some text in a lossy way
    that's good for counting word frequencies.

    In particular:

    - Any sequence of 2 or more adjacent digits, possibly with intervening
      punctuation such as a decimal point, will replace each digit with '0'
      so that frequencies for numbers don't have to be counted separately.

      This is similar to but not quite identical to the word2vec Google News
      data, which replaces digits with '#' in tokens with more than one digit.

    - In Chinese, unless Traditional Chinese is specifically requested using
      'zh-Hant', all characters will be converted to Simplified Chinese.
    """
    global _simplify_chinese

    info = get_language_info(lang)
    tokens = tokenize(text, lang, include_punctuation, external_wordlist)

    if info['lookup_transliteration'] == 'zh-Hans':
        from wordfreq.chinese import simplify_chinese as _simplify_chinese
        tokens = [_simplify_chinese(token) for token in tokens]

    return [smash_numbers(token) for token in tokens]
