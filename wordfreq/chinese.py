from pkg_resources import resource_filename
import jieba
import msgpack
import gzip

DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh.txt')
SIMP_MAP_FILENAME = resource_filename('wordfreq', 'data/_chinese_mapping.msgpack.gz')
SIMPLIFIED_MAP = msgpack.load(gzip.open(SIMP_MAP_FILENAME), encoding='utf-8')
jieba_tokenizer = None


def simplify_chinese(text):
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


def jieba_tokenize(text):
    """
    Tokenize the given text into tokens whose word frequencies can probably
    be looked up. This uses Jieba, a word-frequency-based tokenizer.

    We tell Jieba to default to using wordfreq's own Chinese wordlist, and not
    to infer unknown words using a hidden Markov model. This ensures that the
    multi-character tokens that it outputs will be ones whose word frequencies
    we can look up.
    """
    global jieba_tokenizer
    if jieba_tokenizer is None:
        jieba_tokenizer = jieba.Tokenizer(dictionary=DICT_FILENAME)
    return jieba_tokenizer.lcut(simplify_chinese(text), HMM=False)
