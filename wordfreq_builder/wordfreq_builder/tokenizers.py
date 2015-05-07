from lumi_science.text_readers.rosette_readers import RosetteReader
from html.entities import name2codepoint
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


NON_PUNCT_RE = re.compile('[0-9A-Za-z\xc0-\u1fff\u2070-\u2fff\u301f-\ufeff０-９Ａ-Ｚａ-ｚ\uff66-\U0002ffff]')

EMOTICON_RANGE = '\u2600-\u26ff\U0001F000-\U0001F7FF'
RETOKENIZE_RE = re.compile('[{0}#@/]|[^{0}#@/ ]+'.format(EMOTICON_RANGE))


def last_tab(line):
    """
    Read lines by keeping only the last tab-separated value.
    """
    return line.split('\t')[-1].strip()


def lowercase_text_filter(token):
    if NON_PUNCT_RE.search(token):
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


def retokenize(text):
    text = fix_entities(text)
    tokens = RETOKENIZE_RE.findall(text)
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
                for token in retokenize(line.strip()):
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
                        filtered = [token_filter(t) for t in tokens]
                        filtered = [t for t in filtered if t is not None]
                        for token in filtered:
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


def treebank_surface_tokenizer(text, language='en'):
    """
    This is a simplified version of the Treebank tokenizer in NLTK.

    NLTK's version depends on the text first having been sentence-tokenized
    using Punkt, which is a statistical model that we'd rather not implement
    here. The main reason to use Punkt first is to disambiguate periods that
    are sentence-ending from those that are part of abbreviations.

    NLTK's tokenizer thus assumes that any periods that appear in the middle
    of the text are meant to be there, and leaves them attached to words. We
    can skip the complication of Punkt at the cost of altering abbreviations
    such as "U.S.".

    NLTK also splits contractions that lack apostrophes, giving pseudo-words
    as a result -- for example, it splits "wanna" into "wan" and "na", which
    are supposed to be considered unusual surface forms of "want" and "to".
    We just leave it as the word "wanna".

    The language will just be returned, as this function isn't doing any
    language detection. It defaults to 'en', as English is the language that
    Treebank tokenization is designed for.
    """
    #starting quotes
    text = re.sub(r'^\"', r'``', text)
    text = re.sub(r'(``)', r' \1 ', text)
    text = re.sub(r'([ (\[{<])"', r'\1 `` ', text)

    #punctuation
    text = re.sub(r'([:,])([^\d])', r' \1 \2', text)
    text = re.sub(r'\.\.\.', r' ... ', text)
    text = re.sub(r'[;@#$%&]', r' \g<0> ', text)

    # The following rule was modified from NLTK, which only separated periods
    # at the end of the text. We simply made whitespace an alternative to the
    # text-ending symbol $.
    text = re.sub(r'([^\.])(\.)([\]\)}>"\']*)(\s|$)', r'\1 \2\3 ', text)
    text = re.sub(r'[?!]', r' \g<0> ', text)

    text = re.sub(r"([^'])' ", r"\1 ' ", text)

    #parens, brackets, etc.
    text = re.sub(r'[\]\[\(\)\{\}\<\>]', r' \g<0> ', text)
    text = re.sub(r'--', r' -- ', text)

    #add extra space to make things easier
    text = " " + text + " "

    #ending quotes
    text = re.sub(r'"', " '' ", text)
    text = re.sub(r'(\S)(\'\')', r'\1 \2 ', text)

    #contractions
    text = re.sub(r"([^' ])('[sS]|'[mM]|'[dD]|') ", r"\1 \2 ", text)
    text = re.sub(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) ", r"\1 \2 ",
                  text)

    return text.split(), language
