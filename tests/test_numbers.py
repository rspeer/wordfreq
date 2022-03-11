from wordfreq import word_frequency
from wordfreq.numbers import digit_freq, smash_numbers
from pytest import approx


def test_number_smashing():
    assert smash_numbers("1") == "1"
    assert smash_numbers("3.14") == "0.00"
    assert smash_numbers("24601") == "00000"


def test_decimals():
    assert word_frequency("3.14", "el") > word_frequency("4.14", "el")
    assert word_frequency("3.14", "el") == word_frequency("3.15", "el")
    assert word_frequency("3,14", "de") > word_frequency("4,14", "de")
    assert word_frequency("3,14", "de") == word_frequency("3,15", "de")


def test_eastern_arabic():
    assert word_frequency("٥٤", "ar") == word_frequency("٥٣", "ar")
    assert word_frequency("٤٣", "ar") > word_frequency("٥٤", "ar")


def test_year_distribution():
    assert word_frequency("2010", "en") > word_frequency("1010", "en")
    assert word_frequency("2010", "en") > word_frequency("3010", "en")


def test_boundaries():
    assert word_frequency("9", "en") > word_frequency("10", "en")
    assert word_frequency("99", "en") > word_frequency("100", "en")
    assert word_frequency("999", "en") > word_frequency("1000", "en")
    assert word_frequency("9999", "en") > word_frequency("10000", "en")


def test_multiple_words():
    once = word_frequency("2015b", "en")
    twice = word_frequency("2015b 2015b", "en")
    assert once == approx(2 * twice)


def test_distribution():
    assert word_frequency("24601", "en") > word_frequency("90210", "en")
    assert word_frequency("7", "en") > word_frequency("007", "en")
    assert word_frequency("404", "en") == word_frequency("418", "en")


def test_3digit_sum():
    """
    Test that the probability distribution given you have a 4-digit sequence
    adds up to approximately 1.
    """
    three_digit_sum = sum(digit_freq(f"{num:03d}") for num in range(0, 1000))
    assert three_digit_sum == approx(1.0)


def test_4digit_sum():
    """
    Test that the probability distribution given you have a 4-digit sequence
    adds up to approximately 1.
    """
    four_digit_sum = sum(digit_freq(f"{num:04d}") for num in range(0, 10000))
    assert 0.999 < four_digit_sum < 1.0
