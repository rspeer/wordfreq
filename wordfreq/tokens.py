import regex
import unicodedata


TOKEN_RE = regex.compile(r"""
    # Case 1: a special case for Chinese and Japanese
    # -----------------------------------------------

    # When we see characters that are Han ideographs (\p{IsIdeo}) or hiragana
    # (\p{Script=Hiragana}), we allow a sequence of those characters to be
    # glued together as a single token. Without this case, the standard rule
    # (case 2) would make each character a separate token. This would be the
    # correct behavior for word-wrapping, but a messy failure mode for NLP
    # tokenization.
    #
    # It is, of course, better to use a tokenizer that is designed for Chinese
    # or Japanese text. This is effectively a fallback for when the wrong
    # tokenizer is used.
    #
    # This rule is listed first so that it takes precedence.

    [\p{IsIdeo}\p{Script=Hiragana}]+ |

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

ARABIC_MARK_RE = regex.compile(r'[\p{Mn}\N{ARABIC TATWEEL}]', regex.V1)


def simple_tokenize(text):
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

    - It outputs only the tokens that start with a word-like character, or
      miscellaneous symbols such as emoji.

    - It breaks on all spaces, even the "non-breaking" ones.
    """
    text = unicodedata.normalize('NFC', text)
    return [token.strip("'").casefold() for token in TOKEN_RE.findall(text)]


def remove_arabic_marks(text):
    """
    Remove decorations from Arabic words:

    - Combining marks of class Mn, which tend to represent non-essential
      vowel markings.
    - Tatweels, horizontal segments that are used to extend or justify a
      word.
    """
    return ARABIC_MARK_RE.sub('', text)


mecab_tokenize = None
def tokenize(text, lang):
    """
    Tokenize this text in a way that's relatively simple but appropriate for
    the language.

    So far, this means:

    - Chinese is presumed to already be tokenized. (Sorry. It's hard.)
    - Japanese will be delegated to the external mecab-python module.
    - Chinese or Japanese texts that aren't identified as the appropriate
      language will only split on punctuation and script boundaries, giving
      you untokenized globs of characters that probably represent many words.
    - All other languages will be tokenized using a regex that mostly
      implements the Word Segmentation section of Unicode Annex #29.
      See `simple_tokenize` for details.

    Additionally, the text will be case-folded to lowercase, and text marked
    as Arabic will be normalized more strongly and have combining marks and
    tatweels removed.

    Strings that are looked up in wordfreq will be run through this function
    first, so that they can be expected to match the data.
    """
    if lang == 'ja':
        global mecab_tokenize
        if mecab_tokenize is None:
            from wordfreq.mecab import mecab_tokenize
        return mecab_tokenize(text)

    if lang == 'ar':
        text = remove_arabic_marks(unicodedata.normalize('NFKC', text))

    return simple_tokenize(text)

