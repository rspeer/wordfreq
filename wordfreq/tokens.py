import regex
import unicodedata


mecab_tokenize = None
jieba_tokenize = None

# See the documentation inside TOKEN_RE for why we have to handle these
# scripts specially.
SPACELESS_SCRIPTS = [
    'Hiragana',
    'Thai',  # Thai script
    'Khmr',  # Khmer script
    'Laoo',  # Lao script
    'Mymr',  # Burmese script
    'Tale',  # Tai Le script
    'Talu',  # Tai Lü script
    'Lana',  # Lanna script
]

ABJAD_LANGUAGES = {
    'ar', 'bal', 'fa', 'ku', 'ps', 'sd', 'tk', 'ug', 'ur', 'he', 'yi'
}


def _make_spaceless_expr():
    pieces = [r'\p{IsIdeo}'] + [r'\p{Script=%s}' % script_code for script_code in SPACELESS_SCRIPTS]
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

    [\w\p{So}]

    # The rest of the token matches characters that are not any sort of space
    # (\S) and do not cause word breaks according to the Unicode word
    # segmentation heuristic (\B), or are categorized as Marks (\p{M}).

    (?:\B\S|\p{M})*
""".replace('<SPACELESS>', SPACELESS_EXPR), regex.V1 | regex.WORD | regex.VERBOSE)

TOKEN_RE_WITH_PUNCTUATION = regex.compile(r"""
    [<SPACELESS>]+ |
    [\p{punct}]+ |
    \S(?:\B\S|\p{M})*
""".replace('<SPACELESS>', SPACELESS_EXPR), regex.V1 | regex.WORD | regex.VERBOSE)

MARK_RE = regex.compile(r'[\p{Mn}\N{ARABIC TATWEEL}]', regex.V1)


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

    - It aims to keep marks together with words, so that they aren't erroneously
      split off as punctuation in languages such as Hindi.

    - It keeps Southeast Asian scripts, such as Thai, glued together. This yields
      tokens that are much too long, but the alternative is that every character
      would end up in its own token, which is worse.
    """
    text = unicodedata.normalize('NFC', text)
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.strip("'").casefold() for token in token_expr.findall(text)]


def turkish_tokenize(text, include_punctuation=False):
    """
    Like `simple_tokenize`, but modifies i's so that they case-fold correctly
    in Turkish, and modifies 'comma-below' characters to use cedillas.
    """
    text = unicodedata.normalize('NFC', text).replace('İ', 'i').replace('I', 'ı')
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [
        commas_to_cedillas(token.strip("'").casefold())
        for token in token_expr.findall(text)
    ]


def romanian_tokenize(text, include_punctuation=False):
    """
    Like `simple_tokenize`, but modifies the letters ş and ţ (with cedillas)
    to use commas-below instead.
    """
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [
        cedillas_to_commas(token.strip("'").casefold())
        for token in token_expr.findall(text)
    ]


def tokenize_mecab_language(text, lang, include_punctuation=False):
    """
    Tokenize Japanese or Korean text, initializing the MeCab tokenizer if necessary.
    """
    global mecab_tokenize
    if not (lang == 'ja' or lang == 'ko'):
        raise ValueError("Only Japanese and Korean can be tokenized using MeCab")
    if mecab_tokenize is None:
        from wordfreq.mecab import mecab_tokenize
    tokens = mecab_tokenize(text, lang)
    token_expr = TOKEN_RE_WITH_PUNCTUATION if include_punctuation else TOKEN_RE
    return [token.casefold() for token in tokens if token_expr.match(token)]


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


def remove_marks(text):
    """
    Remove decorations from words in abjad scripts:

    - Combining marks of class Mn, which tend to represent non-essential
      vowel markings.
    - Tatweels, horizontal segments that are used to extend or justify an
      Arabic word.
    """
    return MARK_RE.sub('', text)


def commas_to_cedillas(text):
    """
    Convert s and t with commas (ș and ț) to cedillas (ş and ţ), which is
    preferred in Turkish.

    Only the lowercase versions are replaced, because this assumes the
    text has already been case-folded.
    """
    return text.replace(
        '\N{LATIN SMALL LETTER S WITH COMMA BELOW}',
        '\N{LATIN SMALL LETTER S WITH CEDILLA}'
    ).replace(
        '\N{LATIN SMALL LETTER T WITH COMMA BELOW}',
        '\N{LATIN SMALL LETTER T WITH CEDILLA}'
    )


def cedillas_to_commas(text):
    """
    Convert s and t with cedillas (ş and ţ) to commas (ș and ț), which is
    preferred in Romanian.

    Only the lowercase versions are replaced, because this assumes the
    text has already been case-folded.
    """
    return text.replace(
        '\N{LATIN SMALL LETTER S WITH CEDILLA}',
        '\N{LATIN SMALL LETTER S WITH COMMA BELOW}'
    ).replace(
        '\N{LATIN SMALL LETTER T WITH CEDILLA}',
        '\N{LATIN SMALL LETTER T WITH COMMA BELOW}'
    )


def tokenize(text, lang, include_punctuation=False, external_wordlist=False):
    """
    Tokenize this text in a way that's relatively simple but appropriate for
    the language. Strings that are looked up in wordfreq will be run through
    this function first, so that they can be expected to match the data.

    Some of the processing steps are specific to one language, such as Chinese,
    but what broadly happens to the text depends on what general writing system
    the language uses, out of these categories:

    - Alphabetic scripts: English, Spanish, Russian, etc.
    - Abjad scripts: Arabic, Hebrew, Persian, Urdu, etc.
    - CJK scripts: Chinese, Japanese, Korean
    - Brahmic scripts: Hindi, Tamil, Telugu, Kannada, etc.


    Alphabetic scripts
    ------------------

    The major alphabetic scripts -- Latin, Cyrillic, and Greek -- cover most
    European languages, which are relatively straightforward to tokenize.

    Text in these scripts will be normalized to NFC form, then passed
    through a regular expression that implements the Word Segmentation section
    of Unicode Annex #29, and then case-folded to lowercase.

    The effect is mostly to split the text on spaces and punctuation. There are
    some subtleties involving apostrophes inside words, which the regex will
    only split when they occur before a vowel. ("Hasn't" is one token, but
    "l'enfant" is two.)

    If the language is Turkish, the case-folding rules will take this into
    account, so that capital I and İ map to ı and i respectively.


    Abjad scripts
    -------------

    Languages in the Arabic or Hebrew scripts are written with optional vowel
    marks, and sometimes other decorative markings and ligatures. In these
    languages:

    - The text will be NFKC-normalized, which is a stronger and lossier form
      than NFC. Here its purpose is to reduce ligatures to simpler characters.

    - Marks will be removed, as well as the Arabic tatweel (an extension of
      a word that is used for justification or decoration).

    After these steps, the text will go through the same process as the
    alphabetic scripts above.


    CJK scripts
    -----------

    In the CJK languages, word boundaries can't usually be identified by a
    regular expression. Instead, there needs to be some language-specific
    handling.

    - Chinese text first gets converted to a canonical representation we call
      "Oversimplified Chinese", where all characters are replaced by their
      Simplified Chinese form, no matter what, even when this misspells a word or
      a name. This representation is then tokenized using the Jieba tokenizer,
      trained on the list of Chinese words that can be looked up in wordfreq.

    - Japanese and Korean will be NFKC-normalized, then tokenized using the
      MeCab tokenizer, using dictionary files that are included in this
      package.

    The `external_wordlist` option only affects Chinese tokenization.  If it's
    True, then wordfreq will not use its own Chinese wordlist for tokenization.
    Instead, it will use the large wordlist packaged with the Jieba tokenizer,
    and it will leave Traditional Chinese characters as is. This will probably
    give more accurate tokenization, but the resulting tokens won't necessarily
    have word frequencies that can be looked up.

    If you end up seeing tokens that are entire phrases or sentences glued
    together, that probably means you passed in CJK text with the wrong
    language code.


    Brahmic scripts and other languages
    -----------------------------------

    Any kind of language not previously mentioned will just go through the same
    tokenizer that alphabetic languages use.

    We've tweaked this tokenizer for the case of Indic languages in Brahmic
    scripts, such as Hindi, Tamil, and Telugu, so that we can handle these
    languages where the default Unicode algorithm wouldn't quite work.

    Southeast Asian languages, such as Thai, Khmer, Lao, and Myanmar, are
    written in Brahmic-derived scripts, but usually *without spaces*. wordfreq
    does not support these languages yet. It will split on spaces and
    punctuation, giving tokens that are far too long.
    """
    if lang == 'ja' or lang == 'ko':
        return tokenize_mecab_language(text, lang, include_punctuation)
    elif lang == 'zh':
        return chinese_tokenize(text, include_punctuation, external_wordlist)
    elif lang == 'tr':
        return turkish_tokenize(text, include_punctuation)
    elif lang == 'ro':
        return romanian_tokenize(text, include_punctuation)
    elif lang in ABJAD_LANGUAGES:
        text = remove_marks(unicodedata.normalize('NFKC', text))
        return simple_tokenize(text, include_punctuation)
    else:
        return simple_tokenize(text, include_punctuation)

