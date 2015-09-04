from pkg_resources import resource_filename
from wordfreq._chinese_mapping import SIMPLIFIED_MAP
import jieba


jieba_initialized = False


def simplify_chinese(text):
    return text.translate(SIMPLIFIED_MAP).casefold()


def chinese_tokenize(text):
    global jieba_initialized
    if not jieba_initialized:
        jieba.set_dictionary(resource_filename('wordfreq', 'data/jieba.txt'))
        jieba_initialized = True
    return list(jieba.cut(simplify_chinese(text)))

