# coding: utf-8
from unicodedata import normalize
from ftfy.fixes import remove_unsafe_private_use


def standardize_word(word):
    u"""
    Apply various normalizations to the text. In languages where this is
    relevant, it will end up in all lowercase letters, with pre-composed
    diacritics.

    Some language-specific gotchas:

    - Words ending with a capital "Σ" in Greek have a lowercase version that
      ends with "ς" on Python 3, but "σ" on Python 2. (Python 3 is
      orthographically correct.) This will lead to different frequencies on
      such Greek words, and different numbers of words in total.

    - Words containing a capital "I" in Turkish will be normalized to a
      lowercase "i", incorrectly, instead of "ı". The effective result is
      that the capitalized versions will not share a word count with the
      lowercase versions.
    """
    return normalize('NFKC', remove_unsafe_private_use(word)).lower()
