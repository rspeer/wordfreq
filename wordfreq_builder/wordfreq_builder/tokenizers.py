from lumi_science.text_readers.rosette_readers import RosetteReader
from html.entities import name2codepoint
from wordfreq import tokenize, TOKEN_RE
import re


ROSETTE = RosetteReader()


# Some of Rosette's language codes are incorrect. For example, 'zh_sc' should
# mean "Chinese as used in Seychelles", which is kind of nonsense. What Rosette
# really means is "Simplified Chinese", whose code is 'zh-Hans'.
ROSETTE_LANG_MAP = {
    'zh_sc': 'zh-Hans',
    'zh_tc': 'zh-Hant',
    'en_uc': 'en',
}


EMOTICON_RANGE = '\u2600-\u26ff\U0001F000-\U0001F7FF'
ROSETTE_RETOKENIZE_RE = re.compile('[{0}#@/]|[^{0}#@/ ]+'.format(EMOTICON_RANGE))


def last_tab(line):
    """
    Read lines by keeping only the last tab-separated value.
    """
    return line.split('\t')[-1].strip()


def lowercase_text_filter(token):
    if TOKEN_RE.search(token):
        return token.lower()
    else:
        return None


def is_url(token):
    return token.startswith('http:') or token.startswith('https:')


def pretokenize_file(in_filename, out_prefix, tokenizer, line_reader=last_tab):
    """
    Process a file by running it through the given tokenizer, sorting the
    results by the language of each line, and inserting spaces into lines
    to mark the token boundaries. This computes the 'hard part' of
    tokenization and allows the results to be saved, so that we can change
    the finer details of the output without re-running everything.
    """
    out_files = {}
    for line in open(in_filename, encoding='utf-8'):
        text = line_reader(line)
        tokens, language = tokenizer(text)
        tokenized = ' '.join(tokens)
        if language is not None:
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


def retokenize_rosette(text):
    text = fix_entities(text)
    tokens = ROSETTE_RETOKENIZE_RE.findall(text)
    skip_next = False
    for token in tokens:
        if token == '/' or token == '@':
            # Avoid idiosyncratic tokens such as URLs and
            # usernames
            skip_next = True
        elif skip_next:
            skip_next = False
        else:
            if not is_url(token):
                filtered = lowercase_text_filter(token)
                if filtered:
                    yield filtered


def retokenize_file(in_filename, out_filename):
    """
    Process a file that has been tokenized (by inserting spaces) in a
    language-specific way by Rosette.
    """
    with open(in_filename, encoding='utf-8') as in_file:
        with open(out_filename, 'w', encoding='utf-8') as out_file:
            for line in in_file:
                skip_next = False
                for token in retokenize_rosette(line.strip()):
                    if skip_next:
                        skip_next = False
                    elif token == '/' or token == '@':
                        # Avoid idiosyncratic tokens such as URLs and
                        # usernames
                        skip_next = True
                    elif lowercase_text_filter(token):
                        print(token, file=out_file)


def monolingual_tokenize_file(in_filename, out_filename, language,
                              tokenizer, line_reader=last_tab,
                              token_filter=lowercase_text_filter,
                              sample_proportion=100):
    with open(in_filename, encoding='utf-8', errors='replace') as in_file:
        with open(out_filename, 'w', encoding='utf-8') as out_file:
            for i, line in enumerate(in_file):
                if i % sample_proportion == 0:
                    text = line_reader(line)
                    tokens, line_language = tokenizer(text)
                    if line_language == language:
                        for token in tokens:
                            print(token, file=out_file)


def rosette_surface_tokenizer(text):
    try:
        analysis, lang = ROSETTE.rosette.analyze(text)
    except (RuntimeError, UnicodeError):
        # Our Rosette interface throws errors given arbitrary data. :(
        return text, None
    language = ROSETTE_LANG_MAP.get(lang, lang)
    tokens = []
    for (stem, pos, span) in analysis:
        surface_text = text[span[0]:span[1]]
        tokens.append(surface_text)
    return tokens, language
