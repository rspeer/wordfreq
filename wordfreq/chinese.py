from pkg_resources import resource_filename
import jieba
import msgpack
import gzip

DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh.txt')
SIMP_MAP_FILENAME = resource_filename('wordfreq', 'data/_chinese_mapping.msgpack.gz')
SIMPLIFIED_MAP = msgpack.load(gzip.open(SIMP_MAP_FILENAME), encoding='utf-8')
JIEBA_TOKENIZER = jieba.Tokenizer(dictionary=DICT_FILENAME)


def simplify_chinese(text):
    return text.translate(SIMPLIFIED_MAP).casefold()


def jieba_tokenize(text):
    return JIEBA_TOKENIZER.lcut(simplify_chinese(text), HMM=False)

