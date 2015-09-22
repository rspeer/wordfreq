from pkg_resources import resource_filename
import jieba
import msgpack
import gzip

jieba_tokenizer = None
simplified_map = None
DICT_FILENAME = resource_filename('wordfreq', 'data/jieba_zh.txt')
SIMP_MAP_FILENAME = resource_filename('wordfreq', 'data/_chinese_mapping.msgpack.gz')


def simplify_chinese(text):
    global simplified_map
    if simplified_map is None:
        simplified_map = msgpack.load(gzip.open(SIMP_MAP_FILENAME), encoding='utf-8')
    return text.translate(simplified_map).casefold()


def jieba_tokenize(text):
    global jieba_tokenizer
    if jieba_tokenizer is None:
        jieba_tokenizer = jieba.Tokenizer(dictionary=DICT_FILENAME)
    return jieba_tokenizer.lcut(simplify_chinese(text), HMM=False)

