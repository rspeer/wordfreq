from nose.tools import eq_, assert_almost_equal, assert_greater
from wordfreq import tokenize, word_frequency


def test_tokens():
    # Let's test on some Chinese text that has unusual combinations of
    # syllables, because it is about an American vice-president.
    #
    # (He was the Chinese Wikipedia's featured article of the day when I
    # wrote this test.)

    hobart = '加勒特·霍巴特'  # Garret Hobart, or "jiā lè tè huò bā tè".

    # He was the sixth American vice president to die in office.
    fact_simplified  = '他是历史上第六位在任期内去世的美国副总统。'
    fact_traditional = '他是歷史上第六位在任期內去世的美國副總統。'

    # His name breaks into five pieces, with the only piece staying together
    # being the one that means 'Bart'. The dot is not included as a token.
    eq_(
        tokenize(hobart, 'zh'),
        ['加', '勒', '特', '霍', '巴特']
    )

    eq_(
        tokenize(fact_simplified, 'zh'),
        [
         # he / is / in history / #6 / counter for people
         '他', '是',  '历史上', '第六', '位',
         # during / term of office / in / die
         '在', '任期', '内', '去世',
         # of / U.S. / deputy / president
         '的', '美国', '副', '总统'
        ]
    )

    # You match the same tokens if you look it up in Traditional Chinese.
    eq_(tokenize(fact_simplified, 'zh'), tokenize(fact_traditional, 'zh'))
    assert_greater(word_frequency(fact_traditional, 'zh'), 0)


def test_combination():
    xiexie_freq = word_frequency('谢谢', 'zh')   # "Thanks"
    assert_almost_equal(
        word_frequency('谢谢谢谢', 'zh'),
        xiexie_freq / 20
    )
