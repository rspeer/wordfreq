import pytest
from wordfreq import tokenize, word_frequency


def test_tokens():
    assert tokenize("감사합니다", "ko") == ["감사", "합니다"]


def test_combination():
    gamsa_freq = word_frequency("감사", "ko")
    habnida_freq = word_frequency("합니다", "ko")

    assert word_frequency("감사감사", "ko") == pytest.approx(gamsa_freq / 2, rel=0.01)
    assert 1.0 / word_frequency("감사합니다", "ko") == pytest.approx(
        1.0 / gamsa_freq + 1.0 / habnida_freq, rel=0.01
    )
