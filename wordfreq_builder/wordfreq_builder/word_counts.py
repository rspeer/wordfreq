from wordfreq_builder.tokenizers import retokenize
from collections import defaultdict
from operator import itemgetter
from ftfy import fix_text
import csv


def count_tokens(filename):
    counts = defaultdict(int)
    with open(filename, encoding='utf-8') as infile:
        for line in infile:
            for token in retokenize(line.strip()):
                counts[token] += 1
    return counts


def read_freqs(filename, cutoff=2):
    raw_counts = defaultdict(float)
    total = 0.
    with open(filename, encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile)
        for key, strval in reader:
            val = float(strval)
            if val < cutoff:
                break
            for token in retokenize(key):
                token = fix_text(token)
                total += val
                # Use += so that, if we give the reader concatenated files with
                # duplicates, it does the right thing
                raw_counts[token] += val

    freqs = {key: raw_count / total
             for (key, raw_count) in raw_counts.items()}
    return freqs


def merge_freqs(freq_dicts):
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


def write_wordlist(freqs, filename):
    """
    Write a dictionary of either raw counts or frequencies to a file of
    comma-separated values.
    """
    with open(filename, 'w', encoding='utf-8', newline='\n') as outfile:
        writer = csv.writer(outfile)
        items = sorted(freqs.items(), key=itemgetter(1), reverse=True)
        for word, freq in items:
            if not ('"' in word or ',' in word):
                writer.writerow([word, str(freq)])
