from wordfreq import tokenize
from ftfy.fixes import unescape_html
import regex
import pycld2

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
        '\N{HANGUL JUNGSEONG FILLER}'
    ] +
    [chr(65534+65536*x+y) for x in range(17) for y in range(2)]
)
CLD2_BAD_CHARS_RE = regex.compile(CLD2_BAD_CHAR_RANGE)

TWITTER_HANDLE_RE = regex.compile(r'@[\S--\p{punct}]+')
TCO_RE = regex.compile('http(?:s)?://t.co/[a-zA-Z0-9]+')


def cld2_surface_tokenizer(text):
    """
    Uses CLD2 to detect the language and wordfreq tokenizer to create tokens.
    """
    text = unescape_html(text)
    text = TWITTER_HANDLE_RE.sub('', text)
    text = TCO_RE.sub('', text)
    lang = cld2_detect_language(text)
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
    return pycld2.detect(text)[2][0][1]


def tokenize_twitter(in_filename, out_prefix, tokenizer):
    """
    Process a file by running it through the Twitter-specific tokenizer,
    which uses cld2 for language detection, and removes Twitter handles
    and t.co URLs.

    Produces output files that are separated by language, with newlines
    between the tokens.
    """
    out_files = {}
    with open(in_filename, encoding='utf-8') as in_file:
        for line in in_file:
            text = line.split('\t')[-1].strip()
            language, tokens = tokenizer(text)
            if language != 'un':
                tokenized = '\n'.join(tokens)
                out_filename = '%s.%s.txt' % (out_prefix, language)
                if out_filename in out_files:
                    out_file = out_files[out_filename]
                else:
                    out_file = open(out_filename, 'w', encoding='utf-8')
                    out_files[out_filename] = out_file
                print(tokenized, file=out_file)
    for out_file in out_files.values():
        out_file.close()
