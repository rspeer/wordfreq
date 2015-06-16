from wordfreq_builder.tokenizers import cld2_surface_tokenizer, cld2_detect_language
from nose.tools import eq_


def test_tokenizer_1():
    text = '"This is a test," she said, "and I\'ll bet y\'all a lot that it won\'t fail."'
    tokens = [
        'this', 'is', 'a', 'test', 'she', 'said',
        'and', "i'll", 'bet', "y'all", 'a', 'lot', 'that',
        'it', "won't", 'fail',
    ]
    result = cld2_surface_tokenizer(text)
    eq_(result[1], tokens)
    eq_(result[0], 'en')

def test_tokenizer_2():
    text = "i use punctuation informally...see?like this."
    tokens = [
        'i', 'use', 'punctuation', 'informally', 'see',
        'like', 'this'
    ]
    result = cld2_surface_tokenizer(text)
    eq_(result[1], tokens)
    eq_(result[0], 'en')

def test_tokenizer_3():
    text = "@ExampleHandle This parser removes twitter handles!"
    tokens = ['this', 'parser', 'removes', 'twitter', 'handles']
    result = cld2_surface_tokenizer(text)
    eq_(result[1], tokens)
    eq_(result[0], 'en')

def test_tokenizer_4():
    text = "This is a really boring example website http://example.com"
    tokens = ['this', 'is', 'a', 'really', 'boring', 'example', 'website']
    result = cld2_surface_tokenizer(text)
    eq_(result[1], tokens)
    eq_(result[0], 'en')


def test_language_recognizer_1():
    text = "Il est le meilleur livre que je ai jamais lu"
    result = cld2_detect_language(text)
    eq_(result, 'fr')

def test_language_recognizer_2():
    text = """A nuvem de Oort, também chamada de nuvem de Öpik-Oort,
    é uma nuvem esférica de planetesimais voláteis que se acredita
    localizar-se a cerca de 50 000 UA, ou quase um ano-luz, do Sol."""
    result = cld2_detect_language(text)
    eq_(result, 'pt')
