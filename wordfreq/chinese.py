from pkg_resources import resource_filename
from wordfreq._chinese_mapping import SIMPLIFIED_MAP
import jieba


jieba_tokenizer = None
DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh.txt')


def simplify_chinese(text):
    return text.translate(SIMPLIFIED_MAP).casefold()


def jieba_tokenize(text):
    global jieba_tokenizer
    if jieba_tokenizer is None:
        jieba_tokenizer = jieba.Tokenizer(dictionary=DICT_FILENAME)
    return jieba_tokenizer.lcut(simplify_chinese(text), HMM=False)

