from wordfreq import tokenize
from ftfy.fixes import unescape_html
import regex
import pycld2
import langcodes

CLD2_BAD_CHAR_RANGE = "[%s]" % "".join(
    [
        '\x00-\x08',
        '\x0b',
        '\x0e-\x1f',
        '\x7f-\x9f',
        '\ud800-\udfff',
        '\ufdd0-\ufdef',
        '\N{HANGUL FILLER}',
        '\N{HANGUL CHOSEONG FILLER}',
        '\N{HANGUL JUNGSEONG FILLER}',
        '<>'
    ] +
    [chr(65534+65536*x+y) for x in range(17) for y in range(2)]
)
CLD2_BAD_CHARS_RE = regex.compile(CLD2_BAD_CHAR_RANGE)

TWITTER_HANDLE_RE = regex.compile(r'@[\S--\p{punct}]+')
TCO_RE = regex.compile('http(?:s)?://t.co/[a-zA-Z0-9]+')
URL_RE = regex.compile(r'http(?:s)?://[^) ]*')
MARKDOWN_URL_RESIDUE_RE = regex.compile(r'\]\(\)')


# Low-frequency languages tend to be detected incorrectly by cld2. The
# following list of languages are languages that appear in our data with any
# reasonable frequency, and seem to usually be detected *correctly*. These are
# the languages we'll keep in the Reddit and Twitter results.
#
# This list is larger than the list that wordfreq ultimately generates, so we
# can look here as a source of future data.

KEEP_THESE_LANGUAGES = {
    'af', 'ar', 'bs', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fi',
    'fr', 'gl', 'he', 'hi', 'hr', 'hu', 'id', 'is', 'it', 'ja', 'ko', 'lv',
    'ms', 'nl', 'nn', 'no', 'pl', 'pt', 'ro', 'ru', 'sr', 'sv', 'sw', 'tl',
    'tr', 'uk', 'vi'
}

# Semi-frequent languages that are excluded by the above:
#
#   - Chinese, not because it's detected incorrectly, but because we can't
#     handle it until we already have word frequencies
#   - Thai (seems to be detected whenever someone uses Thai characters in
#     an emoticon)
#   - Welsh (which is detected for "ohmygodohmygodohmygod")
#   - Turkmen (detected for ASCII art)
#   - Irish Gaelic (detected for Cthulhu-related text)
#   - Kannada (looks of disapproval)
#   - Lao, Tamil, Xhosa, Slovak (various emoticons and Internet memes)
#   - Breton (the word "memes" itself)


def cld2_surface_tokenizer(text, mode='twitter'):
    """
    Uses CLD2 to detect the language and wordfreq tokenizer to create tokens.

    The `mode` can be 'twitter' or 'reddit', which slightly changes the
    pre-processing of the text.
    """
    text = unescape_html(text)
    if mode == 'twitter':
        text = TWITTER_HANDLE_RE.sub('', text)
        text = TCO_RE.sub('', text)
    elif mode == 'reddit':
        text = URL_RE.sub('', text)
        text = MARKDOWN_URL_RESIDUE_RE.sub(']', text)

    lang = cld2_detect_language(text)

    # If the detected language isn't in our pretty generous list of languages,
    # return no tokens.
    if lang not in KEEP_THESE_LANGUAGES:
        return 'xx', []

    # cld2's accuracy seems to improve dramatically with at least 50
    # bytes of input, so throw away non-English below this length.
    if len(text.encode('utf-8')) < 50 and lang != 'en':
        return 'xx', []

    tokens = tokenize(text, lang)
    return lang, tokens


def cld2_detect_language(text):
    """
    Uses CLD2 to detect the language.
    """
    # Format of pycld2.detect:
    #   (Confident in result: bool,
    #   Number of bytes of text: Int,
    #   Triples of detected languages in order of certainty:
    #       (Language name: str,
    #       Language code: str
    #       Percent of text in this language: float
    #       Confidence score: float))

    text = CLD2_BAD_CHARS_RE.sub('', text)
    lang = pycld2.detect(text)[2][0][1]

    # Normalize the language code: 'iw' becomes 'he', and 'zh-Hant'
    # becomes 'zh'
    code = langcodes.get(lang).language
    return code


def tokenize_by_language(in_filename, out_prefix, tokenizer):
    """
    Process a file by running it through a given tokenizer.

    Produces output files that are separated by language, with spaces
    between the tokens.
    """
    out_files = {}
    with open(in_filename, encoding='utf-8') as in_file:
        for line in in_file:
            text = line.split('\t')[-1].strip()
            language, tokens = tokenizer(text)
            if language != 'un':
                tokenized = ' '.join(tokens)
                out_filename = '%s.%s.txt' % (out_prefix, language)
                if out_filename in out_files:
                    out_file = out_files[out_filename]
                else:
                    out_file = open(out_filename, 'w', encoding='utf-8')
                    out_files[out_filename] = out_file
                print(tokenized, file=out_file)
    for out_file in out_files.values():
        out_file.close()
