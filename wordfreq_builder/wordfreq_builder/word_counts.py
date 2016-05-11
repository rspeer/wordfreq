from wordfreq import simple_tokenize, tokenize
from collections import defaultdict
from operator import itemgetter
from ftfy import fix_text
import math
import csv
import msgpack
import gzip
import regex


# Match common cases of URLs: the schema http:// or https:// followed by
# non-whitespace characters.
URL_RE = regex.compile(r'https?://(?:\S)+')
HAN_RE = regex.compile(r'[\p{Script=Han}]+')


def count_tokens(filename):
    """
    Count tokens that appear in a file, running each line through our
    simple tokenizer.

    URLs will be skipped, and Unicode errors will become separate tokens
    containing '�'.
    """
    counts = defaultdict(int)
    if filename.endswith('gz'):
        infile = gzip.open(filename, 'rt', encoding='utf-8', errors='replace')
    else:
        infile = open(filename, encoding='utf-8', errors='replace')
    for line in infile:
        line = URL_RE.sub('', line.strip())
        for token in simple_tokenize(line):
            counts[token] += 1
    infile.close()
    return counts


def read_values(filename, cutoff=0, max_words=1e8, lang=None):
    """
    Read words and their frequency or count values from a CSV file. Returns
    a dictionary of values and the total of all values.

    Only words with a value greater than or equal to `cutoff` are returned.
    In addition, only up to `max_words` words are read.

    If `cutoff` is greater than 0 or `max_words` is smaller than the list,
    the csv file must be sorted by value in descending order, so that the
    most frequent words are kept.

    If `lang` is given, it will apply language-specific tokenization to the
    words that it reads.
    """
    values = defaultdict(float)
    total = 0.
    with open(filename, encoding='utf-8', newline='') as infile:
        for key, strval in csv.reader(infile):
            val = float(strval)
            key = fix_text(key)
            if val < cutoff or len(values) >= max_words:
                break
            tokens = tokenize(key, lang) if lang is not None else simple_tokenize(key)
            for token in tokens:
                # Use += so that, if we give the reader concatenated files with
                # duplicates, it does the right thing
                values[token] += val
                total += val
    return values, total


def read_freqs(filename, cutoff=0, lang=None):
    """
    Read words and their frequencies from a CSV file, normalizing the
    frequencies to add up to 1.

    Only words with a frequency greater than or equal to `cutoff` are returned.

    If `cutoff` is greater than 0, the csv file must be sorted by frequency
    in descending order.

    If lang is given, read_freqs will apply language specific preprocessing
    operations.
    """
    values, total = read_values(filename, cutoff, lang=lang)
    for word in values:
        values[word] /= total

    if lang == 'en':
        values = correct_apostrophe_trimming(values)

    return values


def freqs_to_cBpack(in_filename, out_filename, cutoff=-600):
    """
    Convert a csv file of words and their frequencies to a file in the
    idiosyncratic 'cBpack' format.

    Only words with a frequency greater than `cutoff` centibels will be
    written to the new file.

    This cutoff should not be stacked with a cutoff in `read_freqs`; doing
    so would skew the resulting frequencies.
    """
    freqs = read_freqs(in_filename, cutoff=0, lang=None)
    cBpack = []
    for token, freq in freqs.items():
        cB = round(math.log10(freq) * 100)
        if cB <= cutoff:
            continue
        neg_cB = -cB
        while neg_cB >= len(cBpack):
            cBpack.append([])
        cBpack[neg_cB].append(token)

    for sublist in cBpack:
        sublist.sort()

    # Write a "header" consisting of a dictionary at the start of the file
    cBpack_data = [{'format': 'cB', 'version': 1}] + cBpack

    with gzip.open(out_filename, 'wb') as outfile:
        msgpack.dump(cBpack_data, outfile)


def merge_counts(count_dicts):
    """
    Merge multiple dictionaries of counts by adding their entries.
    """
    merged = defaultdict(int)
    for count_dict in count_dicts:
        for term, count in count_dict.items():
            merged[term] += count
    return merged


def merge_freqs(freq_dicts):
    """
    Merge multiple dictionaries of frequencies, representing each word with
    the word's average frequency over all sources.
    """
    vocab = set()
    for freq_dict in freq_dicts:
        vocab.update(freq_dict)

    merged = defaultdict(float)
    N = len(freq_dicts)
    for term in vocab:
        term_total = 0.
        for freq_dict in freq_dicts:
            term_total += freq_dict.get(term, 0.)
        merged[term] = term_total / N

    return merged


def write_wordlist(freqs, filename, cutoff=1e-8):
    """
    Write a dictionary of either raw counts or frequencies to a file of
    comma-separated values.

    Keep the CSV format simple by explicitly skipping words containing
    commas or quotation marks. We don't believe we want those in our tokens
    anyway.
    """
    with open(filename, 'w', encoding='utf-8', newline='\n') as outfile:
        writer = csv.writer(outfile)
        items = sorted(freqs.items(), key=itemgetter(1), reverse=True)
        for word, freq in items:
            if freq < cutoff:
                break
            if not ('"' in word or ',' in word):
                writer.writerow([word, str(freq)])


def write_jieba(freqs, filename):
    """
    Write a dictionary of frequencies in a format that can be used for Jieba
    tokenization of Chinese.
    """
    with open(filename, 'w', encoding='utf-8', newline='\n') as outfile:
        items = sorted(freqs.items(), key=lambda item: (-item[1], item[0]))
        for word, freq in items:
            if HAN_RE.search(word):
                # Only store this word as a token if it contains at least one
                # Han character.
                fake_count = round(freq * 1e9)
                print('%s %d' % (word, fake_count), file=outfile)


# APOSTROPHE_TRIMMED_PROB represents the probability that this word has had
# "'t" removed from it, based on counts from Twitter, which we know
# accurate token counts for based on our own tokenizer.

APOSTROPHE_TRIMMED_PROB = {
    'don': 0.99,
    'didn': 1.,
    'can': 0.35,
    'won': 0.74,
    'isn': 1.,
    'wasn': 1.,
    'wouldn': 1.,
    'doesn': 1.,
    'couldn': 1.,
    'ain': 0.99,
    'aren': 1.,
    'shouldn': 1.,
    'haven': 0.96,
    'weren': 1.,
    'hadn': 1.,
    'hasn': 1.,
    'mustn': 1.,
    'needn': 1.,
}


def correct_apostrophe_trimming(freqs):
    """
    If what we got was an English wordlist that has been tokenized with
    apostrophes as token boundaries, as indicated by the frequencies of the
    words "wouldn" and "couldn", then correct the spurious tokens we get by
    adding "'t" in about the proportion we expect to see in the wordlist.

    We could also adjust the frequency of "t", but then we would be favoring
    the token "s" over it, as "'s" leaves behind no indication when it's been
    removed.
    """
    if (freqs.get('wouldn', 0) > 1e-6 and freqs.get('couldn', 0) > 1e-6):
        print("Applying apostrophe trimming")
        for trim_word, trim_prob in APOSTROPHE_TRIMMED_PROB.items():
            if trim_word in freqs:
                freq = freqs[trim_word]
                freqs[trim_word] = freq * (1 - trim_prob)
                freqs[trim_word + "'t"] = freq * trim_prob
    return freqs
