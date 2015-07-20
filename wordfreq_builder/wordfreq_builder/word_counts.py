from wordfreq import simple_tokenize, tokenize
from collections import defaultdict
from operator import itemgetter
from ftfy import fix_text
import math
import csv
import msgpack
import gzip


def count_tokens(filename):
    """
    Count tokens that appear in a file, running each line through our
    simple tokenizer.

    Unicode errors in the input data will become token boundaries.
    """
    counts = defaultdict(int)
    with open(filename, encoding='utf-8', errors='replace') as infile:
        for line in infile:
            for token in simple_tokenize(line):
                counts[token] += 1

    return counts


def read_freqs(filename, cutoff=0, lang=None):
    """
    Read words and their frequencies from a CSV file.

    Only words with a frequency greater than or equal to `cutoff` are returned.

    If `cutoff` is greater than 0, the csv file must be sorted by frequency
    in descending order.
    """
    raw_counts = defaultdict(float)
    total = 0.
    with open(filename, encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile)
        for key, strval in reader:
            val = float(strval)
            if val < cutoff:
                break
                
            tokens = tokenize(key, lang) if lang is not None else simple_tokenize(lang)
            for token in tokens:
                token = fix_text(token)
                total += val
                # Use += so that, if we give the reader concatenated files with
                # duplicates, it does the right thing
                raw_counts[token] += val

    for word in raw_counts:
        raw_counts[word] /= total

    return raw_counts


def freqs_to_cBpack(in_filename, out_filename, cutoff=-600, lang=None):
    """
    Convert a csv file of words and their frequencies to a file in the
    idiosyncratic 'cBpack' format.

    Only words with a frequency greater than `cutoff` centibels will be
    written to the new file.
    """
    freq_cutoff = 10 ** (cutoff / 100.)
    freqs = read_freqs(in_filename, lang, freq_cutoff)
    cBpack = []
    for token, freq in freqs.items():
        cB = round(math.log10(freq) * 100)
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
