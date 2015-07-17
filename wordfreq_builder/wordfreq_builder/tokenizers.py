from html.entities import name2codepoint
from wordfreq import tokenize, TOKEN_RE, NON_PUNCT_RANGE
import re
import pycld2

CLD2_BAD_CHAR_RANGE = "[%s]" % "".join(
    [
        '\x00-\x08',
        '\x0b',
        '\x0e-\x1f',
        '\x7f-\x9f',
        '\ud800-\udfff',
        '\ufdd0-\ufdef'
    ] +
    [chr(65534+65536*x+y) for x in range(17) for y in range(2)]
)
CLD2_BAD_CHARS_RE = re.compile(CLD2_BAD_CHAR_RANGE)

TWITTER_HANDLE_RE = re.compile('@{0}+'.format(NON_PUNCT_RANGE))
TCO_RE = re.compile('http(?:s)?://t.co/[a-zA-Z0-9]+')


def cld2_surface_tokenizer(text):
    """
    Uses CLD2 to detect the language and wordfreq tokenizer to create tokens
    """
    text = fix_entities(text)
    text = TWITTER_HANDLE_RE.sub('', text)
    text = TCO_RE.sub('', text)
    lang = cld2_detect_language(text)
    tokens = tokenize(text, lang)
    return lang, tokens


def cld2_detect_language(text):
    """
    Uses CLD2 to detect the language
    """
    text = CLD2_BAD_CHARS_RE.sub('', text)
    return pycld2.detect(text)[2][0][1]


def tokenize_twitter(in_filename, out_prefix, tokenizer):
    """
    Process a file by running it through the given tokenizer, sorting the
    results by the language of each line, and inserting newlines
    to mark the token boundaries.
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


ENTITY_RE = re.compile(r'& ?(amp|quot|lt|gt) ?;')
def fix_entities(text):
    """
    Fix the few HTML entities that Twitter uses -- even if they've
    already been tokenized.
    """
    def replace_entity(match):
        return chr(name2codepoint[match.group(1)])
    return ENTITY_RE.sub(replace_entity, text)
