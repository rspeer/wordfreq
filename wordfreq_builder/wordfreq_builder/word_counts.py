from wordfreq_builder.tokenizers import treebank_surface_tokenizer
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from unicodedata import normalize
import csv
import sys


def read_counts(path):
    counts = defaultdict(int)
    with path.open(encoding='utf-8', newline='') as infile:
        reader = csv.reader(infile)
        for key, strval in reader:
            val = float(strval)
            # Use += so that, if we give the reader concatenated files with
            # duplicates, it does the right thing
            counts[key] += val
    return counts


def count_languages(counts):
    langcounts = defaultdict(int)
    for key, strval in counts.items():
        val = int(strval)
        text, lang = key.rsplit('|', 1)
        langcounts[lang] += val
    return langcounts


def merge_counts(count_dicts, balance=False):
    merged = defaultdict(float)
    for counts in count_dicts:
        weight = 1
        if balance:
            weight = 1e9 / max(counts.values()) / len(count_dicts)
        for key, val in counts.items():
            merged[key] += val * weight
    return merged


def write_counts(counts, path, cutoff=2):
    print("Writing to %s" % path)
    with path.open('w', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        items = sorted(counts.items(), key=itemgetter(1), reverse=True)
        for word, count in items:
            if count < cutoff:
                # Don't write all the terms that appeared too infrequently
                break
            writer.writerow([word, count])


class WordCountBuilder:
    def __init__(self, unique_docs=True, tokenizer=None):
        self.counts = defaultdict(int)
        self.unique_docs = unique_docs
        if tokenizer is None:
            self.tokenizer = treebank_surface_tokenizer
        else:
            self.tokenizer = tokenizer

    def add_text(self, text):
        text = normalize('NFKC', text).lower()
        try:
            tokens = self.tokenizer(text)
            # print(' '.join(tokens))
        except Exception as e:
            print("Couldn't tokenize due to %r: %s" % (e, text), file=sys.stderr)
            return
        if self.unique_docs:
            tokens = set(tokens)
        for tok in tokens:
            self.counts[tok] += 1

    def count_wikipedia(self, path, glob='*/*'):
        """
        Read a directory of extracted Wikipedia articles. The articles can be
        grouped together into files, in which case they should be separated by
        lines beginning with ##.
        """
        for filepath in sorted(path.glob(glob)):
            print(filepath)
            with filepath.open(encoding='utf-8') as file:
                buf = []
                for line in file:
                    line = line.strip()
                    if line.startswith('##'):
                        self.try_wiki_article(' '.join(buf))
                        buf = []
                    else:
                        buf.append(line)
                self.try_wiki_article(' '.join(buf))

    def try_wiki_article(self, text):
        if len(text) > 1000:
            self.add_text(text)

    def count_twitter(self, path, offset, nsplit):
        with path.open(encoding='utf-8') as file:
            for i, line in enumerate(file):
                if i % nsplit == offset:
                    line = line.strip()
                    text = line.split('\t')[-1]
                    self.add_text(text)

    def save_wordlist(self, path):
        write_counts(self.counts, path)
