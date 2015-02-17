from lumi_science.text_readers.rosette_readers import RosetteReader
import re


ROSETTE = RosetteReader()


def rosette_tokenizer(text):
    analysis, lang = ROSETTE.rosette.analyze(text)
    # I'm aware this doesn't do the right things with multi-word stems.
    # Wordfreq doesn't either. And wordfreq isn't designed to look up
    # multiple words anyway.
    return [stem + '|' + lang for (stem, pos, span) in analysis]


def rosette_surface_tokenizer(text):
    analysis, lang = ROSETTE.rosette.analyze(text)
    return [text[span[0]:span[1]] + '|' + lang for (stem, pos, span) in analysis]


def treebank_surface_tokenizer(text):
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

    return text.split()
