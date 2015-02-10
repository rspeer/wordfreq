from wordfreq_builder.tokenizers import treebank_tokenizer
from collections import defaultdict
from operator import itemgetter
from pathlib import Path
from unicodedata import normalize
import csv


class WordCountBuilder:
    def __init__(self, unique_docs=True, tokenizer=None):
        self.counts = defaultdict(int)
        self.unique_docs = unique_docs
        if tokenizer is None:
            self.tokenizer = treebank_tokenizer
        else:
            self.tokenizer = tokenizer

    def add_text(self, text):
        text = normalize('NFKC', text).lower()
        try:
            tokens = self.tokenizer(text)
        except Exception as e:
            print("Couldn't tokenize due to %r: %s" % (e, text))
            return
        if self.unique_docs:
            tokens = set(tokens)
        for tok in tokens:
            self.counts[tok] += 1

    def count_wikipedia(self, path, glob='*/*'):
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

    def count_twitter(self, path, offset, nsplit):
        with path.open(encoding='utf-8') as file:
            for i, line in enumerate(file):
                if i % nsplit == offset:
                    line = line.strip()
                    text = line.split('\t')[-1]
                    self.add_text(text)

    def try_wiki_article(self, text):
        if len(text) > 1000:
            self.add_text(text)

    def save_wordlist(self, path):
        with path.open('w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            items = sorted(self.counts.items(), key=itemgetter(1), reverse=True)
            for word, count in items:
                if count <= 1:
                    # Don't write all the terms that appeared only once
                    break
                writer.writerow([word, count])


