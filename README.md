wordfreq is a Python library for looking up the frequencies of words in many
languages, based on many sources of data.

Author: Rob Speer


## Installation

wordfreq requires Python 3 and depends on a few other Python modules
(msgpack-python, langcodes, and ftfy). You can install it and its dependencies
in the usual way, either by getting it from pip:

    pip3 install wordfreq

or by getting the repository and running its setup.py:

    python3 setup.py install


## Additional CJK installation

Chinese, Japanese, and Korean have additional external dependencies so that
they can be tokenized correctly. Here we'll explain how to set them up,
in increasing order of difficulty.


### Chinese

To be able to look up word frequencies in Chinese, you need Jieba, a
pure-Python Chinese tokenizer:

    pip3 install jieba


### Japanese

We use MeCab, by Taku Kudo, to tokenize Japanese. To use this in wordfreq, three
things need to be installed:

  * The MeCab development library (called `libmecab-dev` on Ubuntu)
  * The UTF-8 version of the `ipadic` Japanese dictionary
    (called `mecab-ipadic-utf8` on Ubuntu)
  * The `mecab-python3` Python interface

To install these three things on Ubuntu, you can run:

```sh
sudo apt-get install libmecab-dev mecab-ipadic-utf8
pip3 install mecab-python3
```

If you choose to install `ipadic` from somewhere else or from its source code,
be sure it's configured to use UTF-8. By default it will use EUC-JP, which will
give you nonsense results.


### Korean

Korean also uses MeCab, with a Korean dictionary package by Yongwoon Lee and
Yungho Yu. This dictionary is not available as an Ubuntu package.

Here's a process you can use to install the Korean dictionary and the other
MeCab dependencies:

```sh
sudo apt-get install libmecab-dev mecab-utils
pip3 install mecab-python3
wget https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.0.1-20150920.tar.gz
tar xvf mecab-ko-dic-2.0.1-20150920.tar.gz
cd mecab-ko-dic-2.0.1-20150920
./autogen.sh
make
sudo make install
```

If wordfreq cannot find the Japanese or Korean data for MeCab when asked to
tokenize those languages, it will raise an error and show you the list of
paths it searched.

Sorry that this is difficult. We tried to just package the data files we need
with wordfreq, like we do for Chinese, but PyPI would reject the package for
being too large.


## Usage

wordfreq provides access to estimates of the frequency with which a word is
used, in 27 languages (see *Supported languages* below).

It provides three kinds of pre-built wordlists:

- `'combined'` lists, containing words that appear at least once per
  million words, averaged across all data sources.
- `'twitter'` lists, containing words that appear at least once per
  million words on Twitter alone.
- `'large'` lists, containing words that appear at least once per 100
  million words, averaged across all data sources.

The most straightforward function is:

    word_frequency(word, lang, wordlist='combined', minimum=0.0)

This function looks up a word's frequency in the given language, returning its
frequency as a decimal between 0 and 1. In these examples, we'll multiply the
frequencies by a million (1e6) to get more readable numbers:

    >>> from wordfreq import word_frequency
    >>> word_frequency('cafe', 'en') * 1e6
    12.88249551693135

    >>> word_frequency('café', 'en') * 1e6
    3.3884415613920273

    >>> word_frequency('cafe', 'fr') * 1e6
    2.6302679918953817

    >>> word_frequency('café', 'fr') * 1e6
    87.09635899560814


`zipf_frequency` is a variation on `word_frequency` that aims to return the
word frequency on a human-friendly logarithmic scale. The Zipf scale was
proposed by Marc Brysbaert, who created the SUBTLEX lists. The Zipf frequency
of a word is the base-10 logarithm of the number of times it appears per
billion words. A word with Zipf value 6 appears once per thousand words, for
example, and a word with Zipf value 3 appears once per million words.

Reasonable Zipf values are between 0 and 8, but because of the cutoffs
described above, the minimum Zipf value appearing in these lists is 1.0 for the
'large' wordlists and 3.0 for all others. We use 0 as the default Zipf value
for words that do not appear in the given wordlist, although it should mean
one occurrence per billion words.

    >>> from wordfreq import zipf_frequency
    >>> zipf_frequency('the', 'en')
    7.67

    >>> zipf_frequency('word', 'en')
    5.39

    >>> zipf_frequency('frequency', 'en')
    4.19

    >>> zipf_frequency('zipf', 'en')
    0.0

    >>> zipf_frequency('zipf', 'en', wordlist='large')
    1.65


The parameters to `word_frequency` and `zipf_frequency` are:

- `word`: a Unicode string containing the word to look up. Ideally the word
  is a single token according to our tokenizer, but if not, there is still
  hope -- see *Tokenization* below.

- `lang`: the BCP 47 or ISO 639 code of the language to use, such as 'en'.

- `wordlist`: which set of word frequencies to use. Current options are
  'combined', 'twitter', and 'large'.

- `minimum`: If the word is not in the list or has a frequency lower than
  `minimum`, return `minimum` instead. You may want to set this to the minimum
  value contained in the wordlist, to avoid a discontinuity where the wordlist
  ends.

Other functions:

`tokenize(text, lang)` splits text in the given language into words, in the same
way that the words in wordfreq's data were counted in the first place. See
*Tokenization*.

`top_n_list(lang, n, wordlist='combined')` returns the most common *n* words in
the list, in descending frequency order.

    >>> from wordfreq import top_n_list
    >>> top_n_list('en', 10)
    ['the', 'i', 'to', 'a', 'and', 'of', 'you', 'in', 'that', 'is']

    >>> top_n_list('es', 10)
    ['de', 'que', 'la', 'y', 'a', 'en', 'el', 'no', 'los', 'es']

`iter_wordlist(lang, wordlist='combined')` iterates through all the words in a
wordlist, in descending frequency order.

`get_frequency_dict(lang, wordlist='combined')` returns all the frequencies in
a wordlist as a dictionary, for cases where you'll want to look up a lot of
words and don't need the wrapper that `word_frequency` provides.

`supported_languages(wordlist='combined')` returns a dictionary whose keys are
language codes, and whose values are the data file that will be loaded to
provide the requested wordlist in each language.

`random_words(lang='en', wordlist='combined', nwords=5, bits_per_word=12)`
returns a selection of random words, separated by spaces. `bits_per_word=n`
will select each random word from 2^n words.

If you happen to want an easy way to get [a memorable, xkcd-style
password][xkcd936] with 60 bits of entropy, this function will almost do the
job. In this case, you should actually run the similar function `random_ascii_words`,
limiting the selection to words that can be typed in ASCII.

[xkcd936]: https://xkcd.com/936/


## Sources and supported languages

We compiled word frequencies from seven different sources, providing us
examples of word usage on different topics at different levels of formality.
The sources (and the abbreviations we'll use for them) are:

- **LeedsIC**: The Leeds Internet Corpus
- **SUBTLEX**: The SUBTLEX word frequency lists
- **OpenSub**: Data derived from OpenSubtitles but not from SUBTLEX
- **Twitter**: Messages sampled from Twitter's public stream
- **Wpedia**: The full text of Wikipedia in 2015
- **Reddit**: The corpus of Reddit comments through May 2015
- **CCrawl**: Text extracted from the Common Crawl and language-detected with cld2
- **Other**: We get additional English frequencies from Google Books Syntactic
  Ngrams 2013, and Chinese frequencies from the frequency dictionary that
  comes with the Jieba tokenizer.

The following 27 languages are supported, with reasonable tokenization and at
least 3 different sources of word frequencies:

    Language    Code    Sources Large?   SUBTLEX OpenSub LeedsIC Twitter Wpedia  CCrawl  Reddit  Other
    ───────────────────────────────────┼──────────────────────────────────────────────────────────────
    Arabic      ar      5       Yes    │ -       Yes     Yes     Yes     Yes     Yes     -       -
    Bulgarian   bg      3       -      │ -       Yes     -       -       Yes     Yes     -       -
    Catalan     ca      3       -      │ -       Yes     -       Yes     Yes     -       -       -
    Danish      da      3       -      │ -       Yes     -       -       Yes     Yes     -       -
    German      de      5       Yes    │ Yes     -       Yes     Yes     Yes     Yes     -       -
    Greek       el      4       -      │ -       Yes     Yes     -       Yes     Yes     -       -
    English     en      7       Yes    │ Yes     Yes     Yes     Yes     Yes     -       Yes     Google Books
    Spanish     es      6       Yes    │ -       Yes     Yes     Yes     Yes     Yes     Yes     -
    Finnish     fi      3       -      │ -       Yes     -       -       Yes     Yes     -       -
    French      fr      5       Yes    │ -       Yes     Yes     Yes     Yes     Yes     -       -
    Hebrew      he      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Hindi       hi      3       -      │ -       -       -       Yes     Yes     Yes     -       -
    Hungarian   hu      3       -      │ -       Yes     -       -       Yes     Yes     -       -
    Indonesian  id      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Italian     it      5       Yes    │ -       Yes     Yes     Yes     Yes     Yes     -       -
    Japanese    ja      4       -      │ -       -       Yes     Yes     Yes     Yes     -       -
    Korean      ko      3       -      │ -       -       -       Yes     Yes     Yes     -       -
    Malay       ms      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Norwegian   nb[1]   3       -      │ -       Yes     -       -       Yes     Yes     -       -
    Dutch       nl      5       Yes    │ Yes     Yes     -       Yes     Yes     Yes     -       -
    Polish      pl      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Portuguese  pt      5       Yes    │ -       Yes     Yes     Yes     Yes     Yes     -       -
    Romanian    ro      3       -      │ -       Yes     -       -       Yes     Yes     -       -
    Russian     ru      5       Yes    │ -       Yes     Yes     Yes     Yes     Yes     -       -
    Swedish     sv      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Turkish     tr      4       -      │ -       Yes     -       Yes     Yes     Yes     -       -
    Chinese     zh[2]   5       -      │ Yes     -       Yes     -       Yes     Yes     -       Jieba

[1] The Norwegian text we have is specifically written in Norwegian Bokmål, so
we give it the language code 'nb'. We would use 'nn' for Nynorsk, but there
isn't enough data to include it in wordfreq.

[2] This data represents text written in both Simplified and Traditional
Chinese. (SUBTLEX is mostly Simplified, while Wikipedia is mostly Traditional.)
The characters are mapped to one another so they can use the same word
frequency list.

Some languages provide 'large' wordlists, including words with a Zipf frequency
between 1.0 and 3.0. These are available in 9 languages that are covered by
enough data sources.


## Tokenization

wordfreq uses the Python package `regex`, which is a more advanced
implementation of regular expressions than the standard library, to
separate text into tokens that can be counted consistently. `regex`
produces tokens that follow the recommendations in [Unicode
Annex #29, Text Segmentation][uax29], including the optional rule that
splits words between apostrophes and vowels.

There are language-specific exceptions:

- In Arabic and Hebrew, it additionally normalizes ligatures and removes
  combining marks.

- In Japanese and Korean, instead of using the regex library, it uses the
  external library `mecab-python3`. This is an optional dependency of wordfreq,
  and compiling it requires the `libmecab-dev` system package to be installed.

- In Chinese, it uses the external Python library `jieba`, another optional
  dependency.

[uax29]: http://unicode.org/reports/tr29/

When wordfreq's frequency lists are built in the first place, the words are
tokenized according to this function.

Because tokenization in the real world is far from consistent, wordfreq will
also try to deal gracefully when you query it with texts that actually break
into multiple tokens:

    >>> zipf_frequency('New York', 'en')
    5.07
    >>> zipf_frequency('北京地铁', 'zh')  # "Beijing Subway"
    3.58

The word frequencies are combined with the half-harmonic-mean function in order
to provide an estimate of what their combined frequency would be. In Chinese,
where the word breaks must be inferred from the frequency of the resulting
words, there is also a penalty to the word frequency for each word break that
must be inferred.

This method of combining word frequencies implicitly assumes that you're asking
about words that frequently appear together. It's not multiplying the
frequencies, because that would assume they are statistically unrelated. So if
you give it an uncommon combination of tokens, it will hugely over-estimate
their frequency:

    >>> zipf_frequency('owl-flavored', 'en')
    3.19


## License

`wordfreq` is freely redistributable under the MIT license (see
`MIT-LICENSE.txt`), and it includes data files that may be
redistributed under a Creative Commons Attribution-ShareAlike 4.0
license (https://creativecommons.org/licenses/by-sa/4.0/).

`wordfreq` contains data extracted from Google Books Ngrams
(http://books.google.com/ngrams) and Google Books Syntactic Ngrams
(http://commondatastorage.googleapis.com/books/syntactic-ngrams/index.html).
The terms of use of this data are:

    Ngram Viewer graphs and data may be freely used for any purpose, although
    acknowledgement of Google Books Ngram Viewer as the source, and inclusion
    of a link to http://books.google.com/ngrams, would be appreciated.

`wordfreq` also contains data derived from the following Creative Commons-licensed
sources:

- The Leeds Internet Corpus, from the University of Leeds Centre for Translation
  Studies (http://corpus.leeds.ac.uk/list.html)

- The OpenSubtitles Frequency Word Lists, compiled by Hermit Dave
  (https://invokeit.wordpress.com/frequency-word-lists/)

- Wikipedia, the free encyclopedia (http://www.wikipedia.org)

It contains data from various SUBTLEX word lists: SUBTLEX-US, SUBTLEX-UK,
SUBTLEX-CH, SUBTLEX-DE, and SUBTLEX-NL, created by Marc Brysbaert et al.
(see citations below) and available at
http://crr.ugent.be/programs-data/subtitle-frequencies.

I (Rob Speer) have obtained permission by e-mail from Marc Brysbaert to
distribute these wordlists in wordfreq, to be used for any purpose, not just
for academic use, under these conditions:

- Wordfreq and code derived from it must credit the SUBTLEX authors.
- It must remain clear that SUBTLEX is freely available data.

These terms are similar to the Creative Commons Attribution-ShareAlike license.

Some additional data was collected by a custom application that watches the
streaming Twitter API, in accordance with Twitter's Developer Agreement &
Policy. This software gives statistics about words that are commonly used on
Twitter; it does not display or republish any Twitter content.

## Citations to work that wordfreq is built on

- Brysbaert, M. & New, B. (2009). Moving beyond Kucera and Francis: A Critical
  Evaluation of Current Word Frequency Norms and the Introduction of a New and
  Improved Word Frequency Measure for American English. Behavior Research
  Methods, 41 (4), 977-990.
  http://sites.google.com/site/borisnew/pub/BrysbaertNew2009.pdf

- Brysbaert, M., Buchmeier, M., Conrad, M., Jacobs, A. M., Bölte, J., & Böhl, A.
  (2015). The word frequency effect. Experimental Psychology.
  http://econtent.hogrefe.com/doi/abs/10.1027/1618-3169/a000123?journalCode=zea

- Brysbaert, M., Buchmeier, M., Conrad, M., Jacobs, A.M., Bölte, J., & Böhl, A.
  (2011). The word frequency effect: A review of recent developments and
  implications for the choice of frequency estimates in German. Experimental
  Psychology, 58, 412-424.

- Cai, Q., & Brysbaert, M. (2010). SUBTLEX-CH: Chinese word and character
  frequencies based on film subtitles. PLoS One, 5(6), e10729.
  http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0010729

- Dave, H. (2011). Frequency word lists.
  https://invokeit.wordpress.com/frequency-word-lists/

- Davis, M. (2012). Unicode text segmentation. Unicode Standard Annex, 29.
  http://unicode.org/reports/tr29/

- Keuleers, E., Brysbaert, M. & New, B. (2010). SUBTLEX-NL: A new frequency
  measure for Dutch words based on film subtitles. Behavior Research Methods,
  42(3), 643-650.
  http://crr.ugent.be/papers/SUBTLEX-NL_BRM.pdf

- Kudo, T. (2005). Mecab: Yet another part-of-speech and morphological
  analyzer.
  http://mecab.sourceforge.net/

- van Heuven, W. J., Mandera, P., Keuleers, E., & Brysbaert, M. (2014).
  SUBTLEX-UK: A new and improved word frequency database for British English.
  The Quarterly Journal of Experimental Psychology, 67(6), 1176-1190.
  http://www.tandfonline.com/doi/pdf/10.1080/17470218.2013.850521
