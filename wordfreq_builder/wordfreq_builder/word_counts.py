from wordfreq import simple_tokenize
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
    """
    counts = defaultdict(int)
    with open(filename, encoding='utf-8') as infile:
        for line in infile:
            for token in simple_tokenize(line.strip()):
                counts[token] += 1
    return counts


def read_freqs(filename, cutoff=0):
    """
    Read words and their frequencies from a CSV file.

    Only words with a frequency greater than `cutoff` are returned.
    
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
            for token in simple_tokenize(key):
                token = fix_text(token)
                total += val
                # Use += so that, if we give the reader concatenated files with
                # duplicates, it does the right thing
                raw_counts[token] += val

    freqs = {key: raw_count / total
             for (key, raw_count) in raw_counts.items()}
    return freqs


def freqs_to_dBpack(in_filename, out_filename, cutoff=-60):
    """
    Convert a dictionary of word frequencies to a file in the idiosyncratic
    'dBpack' format.
    """
    freq_cutoff = 10 ** (cutoff / 10.)
    freqs = read_freqs(in_filename, freq_cutoff)
    dBpack = []
    for token, freq in freqs.items():
        dB = round(math.log10(freq) * 10)
        if dB >= cutoff:
            neg_dB = -dB
            while neg_dB >= len(dBpack):
                dBpack.append([])
            dBpack[neg_dB].append(token)

    for sublist in dBpack:
        sublist.sort()

    with gzip.open(out_filename, 'wb') as outfile:
        msgpack.dump(dBpack, outfile)


def merge_freqs(freq_dicts):
    """
    Merge multiple dictionaries of frequencies, representing each word with
    the word's average frequency over all sources.
    """
    vocab = set()
    for freq_dict in freq_dicts:
        vocab |= set(freq_dict)

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
