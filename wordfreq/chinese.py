from __future__ import annotations

import gzip

import jieba
import msgpack

from .util import data_path

DICT_FILENAME = data_path("jieba_zh.txt")
ORIG_DICT_FILENAME = data_path("jieba_zh_orig.txt")
SIMP_MAP_FILENAME = data_path("_chinese_mapping.msgpack.gz")
try:
    SIMPLIFIED_MAP = msgpack.load(gzip.open(SIMP_MAP_FILENAME), raw=False, strict_map_key=False)
except TypeError:
    # work around incompatibility between pure-Python msgpack and C msgpack
    SIMPLIFIED_MAP = msgpack.load(gzip.open(SIMP_MAP_FILENAME), raw=False)
jieba_tokenizer: jieba.Tokenizer | None = None
jieba_orig_tokenizer: jieba.Tokenizer | None = None


def simplify_chinese(text: str) -> str:
    """
    Convert Chinese text character-by-character to Simplified Chinese, for the
    purpose of looking up word frequencies.

    This is far too simple to be a proper Chinese-to-Chinese "translation"; it
    will sometimes produce nonsense words by simplifying characters that would
    not be simplified in context, or by simplifying words that would only be
    used in a Traditional Chinese locale. But the resulting text is still a
    reasonable key for looking up word frequenices.
    """
    return text.translate(SIMPLIFIED_MAP).casefold()


def jieba_tokenize(text: str, external_wordlist: bool = False) -> list[str]:
    """
    Tokenize the given text into tokens whose word frequencies can probably
    be looked up. This uses Jieba, a word-frequency-based tokenizer.

    If `external_wordlist` is False, we tell Jieba to default to using
    wordfreq's own Chinese wordlist, and not to infer unknown words using a
    hidden Markov model. This ensures that the multi-character tokens that it
    outputs will be ones whose word frequencies we can look up.

    If `external_wordlist` is True, this will use the largest version of
    Jieba's original dictionary, with HMM enabled, so its results will be
    independent of the data in wordfreq. These results will be better optimized
    for purposes that aren't looking up word frequencies, such as general-
    purpose tokenization, or collecting word frequencies in the first place.
    """
    global jieba_tokenizer, jieba_orig_tokenizer
    if external_wordlist:
        if jieba_orig_tokenizer is None:
            jieba_orig_tokenizer = jieba.Tokenizer(dictionary=ORIG_DICT_FILENAME)
        return jieba_orig_tokenizer.lcut(text)
    else:
        if jieba_tokenizer is None:
            jieba_tokenizer = jieba.Tokenizer(dictionary=DICT_FILENAME)

        # Tokenize the Simplified Chinese version of the text, but return
        # those spans from the original text, even if it's in Traditional
        # Chinese
        tokens = []
        for _token, start, end in jieba_tokenizer.tokenize(simplify_chinese(text), HMM=False):
            tokens.append(text[start:end])
        return tokens
