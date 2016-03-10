import regex
import unicodedata


TOKEN_RE = regex.compile(r"""
    # Case 1: a special case for non-spaced languages
    # -----------------------------------------------

    # When we see characters that are Han ideographs (\p{IsIdeo}), hiragana
    # (\p{Script=Hiragana}), or Thai (\p{Script=Thai}), we allow a sequence
    # of those characters to be glued together as a single token.
    #
    # Without this case, the standard rule (case 2) would make each character
    # a separate token. This would be the correct behavior for word-wrapping,
    # but a messy failure mode for NLP tokenization.
    #
    # It is, of course, better to use a tokenizer that is designed for Chinese,
    # Japanese, or Thai text. This is effectively a fallback for when the wrong
    # tokenizer is used.
    #
    # This rule is listed first so that it takes precedence.

    [\p{IsIdeo}\p{Script=Hiragana}\p{Script=Thai}]+ |

    # Case 2: standard Unicode segmentation
    # -------------------------------------

    # The start of the token must be 'word-like', not punctuation or whitespace
    # or various other things. However, we allow characters of category So
    # (Symbol - Other) because many of these are emoji, which can convey
    # meaning.

    [\w\p{So}]

    # The rest of the token matches characters that are not any sort of space
    # (\S) and do not cause word breaks according to the Unicode word
    # segmentation heuristic (\B).

    (?:\B\S)*
""", regex.V1 | regex.WORD | regex.VERBOSE)

TOKEN_RE_WITH_PUNCTUATION = regex.compile(r"""
    [\p{IsIdeo}\p{Script=Hiragana}]+ |
    [\p{punct}]+ |
    \S(?:\B\S)*
""", regex.V1 | regex.WORD | regex.VERBOSE)

ARABIC_MARK_RE = regex.compile(r'[\p{Mn}\N{ARABIC TATWEEL}]', regex.V1)


def simple_tokenize(text, include_punctuation=False):
    """
    Tokenize the given text using a straightforward, Unicode-aware token
    expression.

    The expression mostly implements the rules of Unicode Annex #29 that
    are contained in the `regex` module's word boundary matching, including
    the refinement that splits words between apostrophes and vowels in order
    to separate tokens such as the French article «l'». Our customizations
    to the expression are:

    - It leaves sequences of Chinese or Japanese characters (specifically, Han
      ideograms and hiragana) relatively untokenized, instead of splitting each
      character into its own token.

    - If `include_punctuation` is False (the default), it outputs only the
      tokens that start with a word-like character, or miscellaneous symbols
      such as emoji. If `include_punctuation` is True, it outputs all non-space
      tokens.

    - It breaks on all spaces, even the "non-breaking" ones.
    """
    text = unicodedata.normalize('NFC', text)
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.strip("'").casefold() for token in token_expr.findall(text)]


def turkish_tokenize(text, include_punctuation=False):
    """
    Like `simple_tokenize`, but modifies i's so that they case-fold correctly
    in Turkish.
    """
    text = unicodedata.normalize('NFC', text).replace('İ', 'i').replace('I', 'ı')
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.strip("'").casefold() for token in token_expr.findall(text)]


mecab_tokenize = None
def japanese_tokenize(text, include_punctuation=False):
    """
    Tokenize Japanese text, initializing the MeCab tokenizer if necessary.
    """
    global mecab_tokenize
    if mecab_tokenize is None:
        from wordfreq.japanese import mecab_tokenize
    tokens = mecab_tokenize(text)
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.casefold() for token in tokens if token_expr.match(token)]


jieba_tokenize = None
def chinese_tokenize(text, include_punctuation=False, external_wordlist=False):
    """
    Tokenize Chinese text, initializing the Jieba tokenizer if necessary.
    """
    global jieba_tokenize
    if jieba_tokenize is None:
        from wordfreq.chinese import jieba_tokenize
    tokens = jieba_tokenize(text, external_wordlist=external_wordlist)
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.casefold() for token in tokens if token_expr.match(token)]


def remove_arabic_marks(text):
    """
    Remove decorations from Arabic words:

    - Combining marks of class Mn, which tend to represent non-essential
      vowel markings.
    - Tatweels, horizontal segments that are used to extend or justify a
      word.
    """
    return ARABIC_MARK_RE.sub('', text)


def tokenize(text, lang, include_punctuation=False, external_wordlist=False):
    """
    Tokenize this text in a way that's relatively simple but appropriate for
    the language. Strings that are looked up in wordfreq will be run through
    this function first, so that they can be expected to match the data.

    Here is what the tokenizer will do, depending on the language:

    - Chinese will be mapped to Simplified Chinese characters and tokenized
      using the Jieba tokenizer, trained on a custom word list of words that
      can be looked up in wordfreq.

    - Japanese will be delegated to the external mecab-python module. It will
      be NFKC normalized, which is stronger than NFC normalization.

    - Chinese or Japanese texts that aren't identified as the appropriate
      language will only split on punctuation and script boundaries, giving
      you untokenized globs of characters that probably represent many words.

    - Arabic will be NFKC normalized, and will have Arabic-specific combining
      marks and tatweels removed.

    - Languages written in cased alphabets will be case-folded to lowercase.

    - Turkish will use a different case-folding procedure, so that capital
      I and İ map to ı and i respectively.

    - Languages besides Japanese and Chinese will be tokenized using a regex
      that mostly implements the Word Segmentation section of Unicode Annex
      #29. See `simple_tokenize` for details.

    The `external_wordlist` option only affects Chinese tokenization.  If it's
    True, then wordfreq will not use its own Chinese wordlist for tokenization.
    Instead, it will use the large wordlist packaged with the Jieba tokenizer,
    and it will leave Traditional Chinese characters as is. This will probably
    give more accurate tokenization, but the resulting tokens won't necessarily
    have word frequencies that can be looked up.
    """
    if lang == 'ja':
        return japanese_tokenize(text, include_punctuation)
    elif lang == 'zh':
        return chinese_tokenize(text, include_punctuation, external_wordlist)
    elif lang == 'tr':
        return turkish_tokenize(text, include_punctuation)
    elif lang == 'ar':
        text = remove_arabic_marks(unicodedata.normalize('NFKC', text))
        return simple_tokenize(text, include_punctuation)
    else:
        return simple_tokenize(text, include_punctuation)

