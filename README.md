wordfreq is a Python library for looking up the frequencies of words in many
languages, based on many sources of data.

Author: Rob Speer


## Installation

wordfreq requires Python 3 and depends on a few other Python modules
(msgpack, langcodes, and regex). You can install it and its dependencies
in the usual way, either by getting it from pip:

    pip3 install wordfreq

or by getting the repository and running its setup.py:

    python3 setup.py install

See [Additional CJK installation](#additional-cjk-installation) for extra
steps that are necessary to get Chinese, Japanese, and Korean word frequencies.


## Usage

wordfreq provides access to estimates of the frequency with which a word is
used, in 35 languages (see *Supported languages* below).

It provides both 'small' and 'large' wordlists:

- The 'small' lists take up very little memory and cover words that appear at
  least once per million words.
- The 'large' lists cover words that appear at least once per 100 million
  words.

The default list is 'best', which uses 'large' if it's available for the
language, and 'small' otherwise.

The most straightforward function for looking up frequencies is:

    word_frequency(word, lang, wordlist='best', minimum=0.0)

This function looks up a word's frequency in the given language, returning its
frequency as a decimal between 0 and 1. In these examples, we'll multiply the
frequencies by a million (1e6) to get more readable numbers:

    >>> from wordfreq import word_frequency
    >>> word_frequency('cafe', 'en') * 1e6
    11.748975549395302

    >>> word_frequency('café', 'en') * 1e6
    3.890451449942805

    >>> word_frequency('cafe', 'fr') * 1e6
    1.4454397707459279

    >>> word_frequency('café', 'fr') * 1e6
    53.70317963702532


`zipf_frequency` is a variation on `word_frequency` that aims to return the
word frequency on a human-friendly logarithmic scale. The Zipf scale was
proposed by Marc Brysbaert, who created the SUBTLEX lists. The Zipf frequency
of a word is the base-10 logarithm of the number of times it appears per
billion words. A word with Zipf value 6 appears once per thousand words, for
example, and a word with Zipf value 3 appears once per million words.

Reasonable Zipf values are between 0 and 8, but because of the cutoffs
described above, the minimum Zipf value appearing in these lists is 1.0 for the
'large' wordlists and 3.0 for 'small'. We use 0 as the default Zipf value
for words that do not appear in the given wordlist, although it should mean
one occurrence per billion words.

    >>> from wordfreq import zipf_frequency
    >>> zipf_frequency('the', 'en')
    7.77

    >>> zipf_frequency('word', 'en')
    5.32

    >>> zipf_frequency('frequency', 'en')
    4.38

    >>> zipf_frequency('zipf', 'en')
    1.32

    >>> zipf_frequency('zipf', 'en', wordlist='small')
    0.0


The parameters to `word_frequency` and `zipf_frequency` are:

- `word`: a Unicode string containing the word to look up. Ideally the word
  is a single token according to our tokenizer, but if not, there is still
  hope -- see *Tokenization* below.

- `lang`: the BCP 47 or ISO 639 code of the language to use, such as 'en'.

- `wordlist`: which set of word frequencies to use. Current options are
  'small', 'large', and 'best'.

- `minimum`: If the word is not in the list or has a frequency lower than
  `minimum`, return `minimum` instead. You may want to set this to the minimum
  value contained in the wordlist, to avoid a discontinuity where the wordlist
  ends.

Other functions:

`tokenize(text, lang)` splits text in the given language into words, in the same
way that the words in wordfreq's data were counted in the first place. See
*Tokenization*.

`top_n_list(lang, n, wordlist='best')` returns the most common *n* words in
the list, in descending frequency order.

    >>> from wordfreq import top_n_list
    >>> top_n_list('en', 10)
    ['the', 'of', 'to', 'and', 'a', 'in', 'i', 'is', 'that', 'for']

    >>> top_n_list('es', 10)
    ['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'no', 'se']

`iter_wordlist(lang, wordlist='best')` iterates through all the words in a
wordlist, in descending frequency order.

`get_frequency_dict(lang, wordlist='best')` returns all the frequencies in
a wordlist as a dictionary, for cases where you'll want to look up a lot of
words and don't need the wrapper that `word_frequency` provides.

`supported_languages(wordlist='best')` returns a dictionary whose keys are
language codes, and whose values are the data file that will be loaded to
provide the requested wordlist in each language.

`random_words(lang='en', wordlist='best', nwords=5, bits_per_word=12)`
returns a selection of random words, separated by spaces. `bits_per_word=n`
will select each random word from 2^n words.

If you happen to want an easy way to get [a memorable, xkcd-style
password][xkcd936] with 60 bits of entropy, this function will almost do the
job. In this case, you should actually run the similar function
`random_ascii_words`, limiting the selection to words that can be typed in
ASCII. But maybe you should just use [xkpa][].

[xkcd936]: https://xkcd.com/936/
[xkpa]: https://github.com/beala/xkcd-password


## Sources and supported languages

This data comes from a Luminoso project called [Exquisite Corpus][xc], whose
goal is to download good, varied, multilingual corpus data, process it
appropriately, and combine it into unified resources such as wordfreq.

[xc]: https://github.com/LuminosoInsight/exquisite-corpus

Exquisite Corpus compiles 8 different domains of text, some of which themselves
come from multiple sources:

- **Wikipedia**, representing encyclopedic text
- **Subtitles**, from OPUS OpenSubtitles 2016 and SUBTLEX
- **News**, from NewsCrawl 2014 and GlobalVoices
- **Books**, from Google Books Ngrams 2012
- **Web** text, from the Leeds Internet Corpus and the MOKK Hungarian Webcorpus
- **Twitter**, representing short-form social media
- **Reddit**, representing potentially longer Internet comments
- **Miscellaneous** word frequencies: in Chinese, we import a free wordlist
  that comes with the Jieba word segmenter, whose provenance we don't really know

The following languages are supported, with reasonable tokenization and at
least 3 different sources of word frequencies:

    Language    Code    #  Large?   WP    Subs  News  Books Web   Twit. Redd. Misc.
    ──────────────────────────────┼────────────────────────────────────────────────
    Arabic      ar      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Bengali     bn      3  -      │ Yes   -     Yes   -     -     Yes   -     -
    Bosnian     bs [1]  3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Bulgarian   bg      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Catalan     ca      4  -      │ Yes   Yes   Yes   -     -     Yes   -     -
    Chinese     zh [3]  6  Yes    │ Yes   -     Yes   Yes   Yes   Yes   -     Jieba
    Croatian    hr [1]  3         │ Yes   Yes   -     -     -     Yes   -     -
    Czech       cs      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Danish      da      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Dutch       nl      4  Yes    │ Yes   Yes   Yes   -     -     Yes   -     -
    English     en      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Finnish     fi      5  Yes    │ Yes   Yes   Yes   -     -     Yes   Yes   -
    French      fr      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    German      de      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Greek       el      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Hebrew      he      4  -      │ Yes   Yes   -     Yes   -     Yes   -     -
    Hindi       hi      3  -      │ Yes   -     -     -     -     Yes   Yes   -
    Hungarian   hu      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Indonesian  id      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Italian     it      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Japanese    ja      5  Yes    │ Yes   Yes   -     -     Yes   Yes   Yes   -
    Korean      ko      4  -      │ Yes   Yes   -     -     -     Yes   Yes   -
    Macedonian  mk      3  -      │ Yes   Yes   Yes   -     -     -     -     -
    Malay       ms      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Norwegian   nb [2]  4  -      │ Yes   Yes   -     -     -     Yes   Yes   -
    Persian     fa      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Polish      pl      5  Yes    │ Yes   Yes   Yes   -     -     Yes   Yes   -
    Portuguese  pt      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Romanian    ro      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Russian     ru      6  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   -     -
    Serbian     sr [1]  3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Spanish     es      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Swedish     sv      4  -      │ Yes   Yes   -     -     -     Yes   Yes   -
    Turkish     tr      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Ukrainian   uk      4  -      │ Yes   Yes   -     -     -     Yes   Yes   -

[1] Bosnian, Croatian, and Serbian use the same underlying word list, because
they share most of their vocabulary and grammar, they were once considered the
same language, and language detection cannot distinguish them. This word list
can also be accessed with the language code `sh`.

[2] The Norwegian text we have is specifically written in Norwegian Bokmål, so
we give it the language code 'nb' instead of the vaguer code 'no'. We would use
'nn' for Nynorsk, but there isn't enough data to include it in wordfreq.

[3] This data represents text written in both Simplified and Traditional
Chinese, with primarily Mandarin Chinese vocabulary. See "Multi-script
languages" below.

Some languages provide 'large' wordlists, including words with a Zipf frequency
between 1.0 and 3.0. These are available in 13 languages that are covered by
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
    5.35
    >>> zipf_frequency('北京地铁', 'zh')  # "Beijing Subway"
    3.54

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
    3.18


## Multi-script languages

Two of the languages we support, Serbian and Chinese, are written in multiple
scripts. To avoid spurious differences in word frequencies, we automatically
transliterate the characters in these languages when looking up their words.

Serbian text written in Cyrillic letters is automatically converted to Latin
letters, using standard Serbian transliteration, when the requested language is
`sr` or `sh`. If you request the word list as `hr` (Croatian) or `bs`
(Bosnian), no transliteration will occur.

Chinese text is converted internally to a representation we call
"Oversimplified Chinese", where all Traditional Chinese characters are replaced
with their Simplified Chinese equivalent, *even if* they would not be written
that way in context. This representation lets us use a straightforward mapping
that matches both Traditional and Simplified words, unifying their frequencies
when appropriate, and does not appear to create clashes between unrelated words.

Enumerating the Chinese wordlist will produce some unfamiliar words, because
people don't actually write in Oversimplified Chinese, and because in
practice Traditional and Simplified Chinese also have different word usage.


## Similar, overlapping, and varying languages

As much as we would like to give each language its own distinct code and its
own distinct word list with distinct source data, there aren't actually sharp
boundaries between languages.

Sometimes, it's convenient to pretend that the boundaries between
languages coincide with national borders, following the maxim that "a language
is a dialect with an army and a navy" (Max Weinreich). This gets complicated
when the linguistic situation and the political situation diverge.
Moreover, some of our data sources rely on language detection, which of course
has no idea which country the writer of the text belongs to.

So we've had to make some arbitrary decisions about how to represent the
fuzzier language boundaries, such as those within Chinese, Malay, and
Croatian/Bosnian/Serbian.  See [Language Log][] for some firsthand reports of
the mutual intelligibility or unintelligibility of languages.

[Language Log]: http://languagelog.ldc.upenn.edu/nll/?p=12633

Smoothing over our arbitrary decisions is the fact that we use the `langcodes`
module to find the best match for a language code. If you ask for word
frequencies in `cmn-Hans` (the fully specific language code for Mandarin in
Simplified Chinese), you will get the `zh` wordlist, for example.


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

It contains data from OPUS OpenSubtitles 2016
(http://opus.lingfil.uu.se/OpenSubtitles2016.php), whose data originates from
the OpenSubtitles project (http://www.opensubtitles.org/).

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


## Citing wordfreq

If you use wordfreq in your research, please cite it! We publish the code
through Zenodo so that it can be reliably cited using a DOI. The current
citation is:

> Robert Speer, Joshua Chin, Andrew Lin, Sara Jewett, & Lance Nathan.
> (2017, September 27). LuminosoInsight/wordfreq: v1.7. Zenodo.
> http://doi.org/10.5281/zenodo.998161


The same citation in BibTex format:

```
@misc{robert_speer_2017_998161,
  author       = {Robert Speer and
                  Joshua Chin and
                  Andrew Lin and
                  Sara Jewett and
                  Lance Nathan},
  title        = {LuminosoInsight/wordfreq: v1.7},
  month        = sep,
  year         = 2017,
  doi          = {10.5281/zenodo.998161},
  url          = {https://doi.org/10.5281/zenodo.998161}
}
```


## Citations to work that wordfreq is built on

- Bojar, O., Chatterjee, R., Federmann, C., Haddow, B., Huck, M., Hokamp, C.,
  Koehn, P., Logacheva, V., Monz, C., Negri, M., Post, M., Scarton, C.,
  Specia, L., & Turchi, M. (2015). Findings of the 2015 Workshop on Statistical
  Machine Translation.
  http://www.statmt.org/wmt15/results.html

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

- Halácsy, P., Kornai, A., Németh, L., Rung, A., Szakadát, I., & Trón, V.
  (2004). Creating open language resources for Hungarian. In Proceedings of the
  4th international conference on Language Resources and Evaluation (LREC2004).
  http://mokk.bme.hu/resources/webcorpus/

- Keuleers, E., Brysbaert, M. & New, B. (2010). SUBTLEX-NL: A new frequency
  measure for Dutch words based on film subtitles. Behavior Research Methods,
  42(3), 643-650.
  http://crr.ugent.be/papers/SUBTLEX-NL_BRM.pdf

- Kudo, T. (2005). Mecab: Yet another part-of-speech and morphological
  analyzer.
  http://mecab.sourceforge.net/

- Lison, P. and Tiedemann, J. (2016). OpenSubtitles2016: Extracting Large
  Parallel Corpora from Movie and TV Subtitles. In Proceedings of the 10th
  International Conference on Language Resources and Evaluation (LREC 2016).
  http://stp.lingfil.uu.se/~joerg/paper/opensubs2016.pdf

- van Heuven, W. J., Mandera, P., Keuleers, E., & Brysbaert, M. (2014).
  SUBTLEX-UK: A new and improved word frequency database for British English.
  The Quarterly Journal of Experimental Psychology, 67(6), 1176-1190.
  http://www.tandfonline.com/doi/pdf/10.1080/17470218.2013.850521
