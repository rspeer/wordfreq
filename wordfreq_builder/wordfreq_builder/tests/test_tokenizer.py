from wordfreq_builder.tokenize import treebank_tokenizer
from nose.tools import eq_


def test_tokenizer_1():
    text = '"This is a test," she said, "and I\'ll bet y\'all $3.50 that it won\'t fail."'
    tokens = [
        "``", 'This', 'is', 'a', 'test', ',', "''", 'she', 'said', ',',
        "``", 'and', 'I', "'ll", 'bet', "y'all", '$', '3.50', 'that',
        'it', 'wo', "n't", 'fail', '.', "''"
    ]
    eq_(treebank_tokenizer(text), tokens)


def test_tokenizer_2():
    text = "i use punctuation informally...see?like this."
    tokens = [
        'i', 'use', 'punctuation', 'informally', '...', 'see', '?',
        'like', 'this', '.'
    ]
    eq_(treebank_tokenizer(text), tokens)
