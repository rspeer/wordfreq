import regex
import unicodedata


# Here's what the following regular expression is looking for:
#
# At the start, it looks for a character in the set [\S--\p{punct}]. \S
# contains non-space characters, and then it subtracts the set of Unicode
# punctuation characters from that set. This is slightly different from \w,
# because it leaves symbols (such as emoji) as tokens.
#
# After it has found one such character, the rest of the token is (?:\B\S)*,
# which continues to consume characters as long as the next character does not
# cause a word break (\B) and is not a space (\S). The individual characters in
# this portion can be punctuation, allowing tokens such as "can't" or
# "google.com".
#
# As a complication, the rest of the token can match a glob of Han ideographs
# (\p{IsIdeo}) and hiragana (\p{Script=Hiragana}). Chinese words are made of
# Han ideographs (but we don't know how many). Japanese words are either made
# of Han ideographs and hiragana (which will be matched by this expression), or
# katakana (which will be matched by the standard Unicode rule).
#
# Without this special case for ideographs and hiragana, the standard Unicode
# rule would put each character in its own token. This actually would be the
# correct behavior for word-wrapping, but it's an ugly failure mode for NLP
# tokenization.

TOKEN_RE = regex.compile(r'[\S--\p{punct}](?:\B\S|[\p{IsIdeo}\p{Script=Hiragana}])*', regex.V1 | regex.WORD)
ARABIC_MARK_RE = regex.compile(r'[[\p{Mn}&&\p{Block=Arabic}]\N{ARABIC TATWEEL}]', regex.V1)


def simple_tokenize(text):
    """
    Tokenize the given text using a straightforward, Unicode-aware token
    expression. It returns non-whitespace tokens that are split at the
    word boundaries defined by Unicode Tech Report #29, as implemented
    by the regex package, except that it leaves Chinese and Japanese
    relatively untokenized.
    """
    text = unicodedata.normalize('NFC', text)
    return [token.casefold() for token in TOKEN_RE.findall(text)]


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
    - All other languages will be tokenized according to UTR #29.

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

