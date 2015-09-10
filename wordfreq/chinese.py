from pkg_resources import resource_filename
from wordfreq._chinese_mapping import SIMPLIFIED_MAP
import jieba


jieba_tokenizer = None
jieba_orig_tokenizer = None
DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh.txt')
ORIG_DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh_orig.txt')


def simplify_chinese(text):
    return text.translate(SIMPLIFIED_MAP).casefold()


def jieba_tokenize(text, external_wordlist=False):
    """
    If `external_wordlist` is False, this will tokenize the given text with our
    custom Jieba dictionary, which contains only the strings that have
    frequencies in wordfreq.

    This is perhaps suboptimal as a general-purpose Chinese tokenizer, but for
    the purpose of looking up frequencies, it's ideal.

    If `external_wordlist` is True, this will use the largest version of
    Jieba's original dictionary, so its results will be independent of the
    data in wordfreq.
    """
    global jieba_tokenizer, jieba_orig_tokenizer
    if external_wordlist:
        if jieba_orig_tokenizer is None:
            jieba_orig_tokenizer = jieba.Tokenizer(dictionary=ORIG_DICT_FILENAME)
        return jieba_orig_tokenizer.lcut(text)
    else:
        if jieba_tokenizer is None:
            jieba_tokenizer = jieba.Tokenizer(dictionary=DICT_FILENAME)
        return jieba_tokenizer.lcut(simplify_chinese(text), HMM=False)
