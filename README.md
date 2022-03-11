wordfreq is a Python library for looking up the frequencies of words in many
languages, based on many sources of data.

Author: Robyn Speer

## Installation

wordfreq requires Python 3 and depends on a few other Python modules
(msgpack, langcodes, and regex). You can install it and its dependencies
in the usual way, either by getting it from pip:

    pip3 install wordfreq

or by getting the repository and installing it for development, using [poetry][]:

    poetry install

[poetry]: https://python-poetry.org/

See [Additional CJK installation](#additional-cjk-installation) for extra
steps that are necessary to get Chinese, Japanese, and Korean word frequencies.

## Usage

wordfreq provides access to estimates of the frequency with which a word is
used, in over 40 languages (see *Supported languages* below). It uses many
different data sources, not just one corpus.

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
frequency as a decimal between 0 and 1.

    >>> from wordfreq import word_frequency
    >>> word_frequency('cafe', 'en')
    1.23e-05

    >>> word_frequency('café', 'en')
    5.62e-06

    >>> word_frequency('cafe', 'fr')
    1.51e-06

    >>> word_frequency('café', 'fr')
    5.75e-05

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
    7.73

    >>> zipf_frequency('word', 'en')
    5.26

    >>> zipf_frequency('frequency', 'en')
    4.36

    >>> zipf_frequency('zipf', 'en')
    1.49

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

## Frequency bins

wordfreq's wordlists are designed to load quickly and take up little space in
the repository.  We accomplish this by avoiding meaningless precision and
packing the words into frequency bins.

In wordfreq, all words that have the same Zipf frequency rounded to the nearest
hundredth have the same frequency. We don't store any more precision than that.
So instead of having to store that the frequency of a word is
.000011748975549395302, where most of those digits are meaningless, we just store
the frequency bins and the words they contain.

Because the Zipf scale is a logarithmic scale, this preserves the same relative
precision no matter how far down you are in the word list. The frequency of any
word is precise to within 1%.

(This is not a claim about *accuracy*, but about *precision*. We believe that
the way we use multiple data sources and discard outliers makes wordfreq a
more accurate measurement of the way these words are really used in written
language, but it's unclear how one would measure this accuracy.)

## The figure-skating metric

We combine word frequencies from different sources in a way that's designed
to minimize the impact of outliers. The method reminds me of the scoring system
in Olympic figure skating:

- Find the frequency of each word according to each data source.
- For each word, drop the sources that give it the highest and lowest frequency.
- Average the remaining frequencies.
- Rescale the resulting frequency list to add up to 1.

## Numbers

These wordlists would be enormous if they stored a separate frequency for every
number, such as if we separately stored the frequencies of 484977 and 484978
and 98.371 and every other 6-character sequence that could be considered a number.

Instead, we have a frequency-bin entry for every number of the same "shape", such
as `##` or `####` or `#.#####`, with `#` standing in for digits. (For compatibility
with earlier versions of wordfreq, our stand-in character is actually `0`.) This
is the same form of aggregation that the word2vec vocabulary does.

Single-digit numbers are unaffected by this process; "0" through "9" have their own
entries in each language's wordlist.

When asked for the frequency of a token containing multiple digits, we multiply
the frequency of that aggregated entry by a distribution estimating the frequency
of those digits. The distribution only looks at two things:

- The value of the first digit
- Whether it is a 4-digit sequence that's likely to represent a year

The first digits are assigned probabilities by Benford's law, and years are assigned
probabilities from a distribution that peaks at the "present". I explored this in
a Twitter thread at <https://twitter.com/r_speer/status/1493715982887571456>.

The part of this distribution representing the "present" is not strictly a peak and
doesn't move forward with time as the present does. Instead, it's a 20-year-long
plateau from 2019 to 2039. (2019 is the last time Google Books Ngrams was updated,
and 2039 is a time by which I will probably have figured out a new distribution.)

Some examples:

    >>> word_frequency("2022", "en")
    5.15e-05
    >>> word_frequency("1922", "en")
    8.19e-06
    >>> word_frequency("1022", "en")
    1.28e-07

Aside from years, the distribution does not care about the meaning of the numbers:

    >>> word_frequency("90210", "en")
    3.34e-10
    >>> word_frequency("92222", "en")
    3.34e-10
    >>> word_frequency("802.11n", "en")
    9.04e-13
    >>> word_frequency("899.19n", "en")
    9.04e-13

The digit rule applies to other systems of digits, and only cares about the numeric
value of the digits:

    >>> word_frequency("٥٤", "ar")
    6.64e-05
    >>> word_frequency("54", "ar")
    6.64e-05

It doesn't know which language uses which writing system for digits:

    >>> word_frequency("٥٤", "en")
    5.4e-05

## Sources and supported languages

This data comes from a Luminoso project called [Exquisite Corpus][xc], whose
goal is to download good, varied, multilingual corpus data, process it
appropriately, and combine it into unified resources such as wordfreq.

[xc]: https://github.com/LuminosoInsight/exquisite-corpus

Exquisite Corpus compiles 8 different domains of text, some of which themselves
come from multiple sources:

- **Wikipedia**, representing encyclopedic text
- **Subtitles**, from OPUS OpenSubtitles 2018 and SUBTLEX
- **News**, from NewsCrawl 2014 and GlobalVoices
- **Books**, from Google Books Ngrams 2012
- **Web** text, from OSCAR
- **Twitter**, representing short-form social media
- **Reddit**, representing potentially longer Internet comments
- **Miscellaneous** word frequencies: in Chinese, we import a free wordlist
  that comes with the Jieba word segmenter, whose provenance we don't really
  know

The following languages are supported, with reasonable tokenization and at
least 3 different sources of word frequencies:

    Language    Code    #  Large?   WP    Subs  News  Books Web   Twit. Redd. Misc.
    ──────────────────────────────┼────────────────────────────────────────────────
    Arabic      ar      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Bangla      bn      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Bosnian     bs [1]  3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Bulgarian   bg      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Catalan     ca      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Chinese     zh [3]  7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   -     Jieba
    Croatian    hr [1]  3         │ Yes   Yes   -     -     -     Yes   -     -
    Czech       cs      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Danish      da      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Dutch       nl      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    English     en      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Finnish     fi      6  Yes    │ Yes   Yes   Yes   -     Yes   Yes   Yes   -
    French      fr      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    German      de      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Greek       el      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Hebrew      he      5  Yes    │ Yes   Yes   -     Yes   Yes   Yes   -     -
    Hindi       hi      4  Yes    │ Yes   -     -     -     Yes   Yes   Yes   -
    Hungarian   hu      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Icelandic   is      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Indonesian  id      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Italian     it      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Japanese    ja      5  Yes    │ Yes   Yes   -     -     Yes   Yes   Yes   -
    Korean      ko      4  -      │ Yes   Yes   -     -     -     Yes   Yes   -
    Latvian     lv      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Lithuanian  lt      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Macedonian  mk      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Malay       ms      3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Norwegian   nb [2]  5  Yes    │ Yes   Yes   -     -     Yes   Yes   Yes   -
    Persian     fa      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Polish      pl      6  Yes    │ Yes   Yes   Yes   -     Yes   Yes   Yes   -
    Portuguese  pt      5  Yes    │ Yes   Yes   Yes   -     Yes   Yes   -     -
    Romanian    ro      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Russian     ru      5  Yes    │ Yes   Yes   Yes   Yes   -     Yes   -     -
    Slovak      sl      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Slovenian   sk      3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Serbian     sr [1]  3  -      │ Yes   Yes   -     -     -     Yes   -     -
    Spanish     es      7  Yes    │ Yes   Yes   Yes   Yes   Yes   Yes   Yes   -
    Swedish     sv      5  Yes    │ Yes   Yes   -     -     Yes   Yes   Yes   -
    Tagalog     fil     3  -      │ Yes   Yes   -     -     Yes   -     -     -
    Tamil       ta      3  -      │ Yes   -     -     -     Yes   Yes   -     -
    Turkish     tr      4  -      │ Yes   Yes   -     -     Yes   Yes   -     -
    Ukrainian   uk      5  Yes    │ Yes   Yes   -     -     Yes   Yes   Yes   -
    Urdu        ur      3  -      │ Yes   -     -     -     Yes   Yes   -     -
    Vietnamese  vi      3  -      │ Yes   Yes   -     -     Yes   -     -     -

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
between 1.0 and 3.0. These are available in 14 languages that are covered by
enough data sources.

## Other functions

`tokenize(text, lang)` splits text in the given language into words, in the same
way that the words in wordfreq's data were counted in the first place. See
*Tokenization*.

`top_n_list(lang, n, wordlist='best')` returns the most common *n* words in
the list, in descending frequency order.

    >>> from wordfreq import top_n_list
    >>> top_n_list('en', 10)
    ['the', 'to', 'and', 'of', 'a', 'in', 'i', 'is', 'for', 'that']

    >>> top_n_list('es', 10)
    ['de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'no', 'un']

`iter_wordlist(lang, wordlist='best')` iterates through all the words in a
wordlist, in descending frequency order.

`get_frequency_dict(lang, wordlist='best')` returns all the frequencies in
a wordlist as a dictionary, for cases where you'll want to look up a lot of
words and don't need the wrapper that `word_frequency` provides.

`available_languages(wordlist='best')` returns a dictionary whose keys are
language codes, and whose values are the data file that will be loaded to
provide the requested wordlist in each language.

`get_language_info(lang)` returns a dictionary of information about how we
preprocess text in this language, such as what script we expect it to be
written in, which characters we normalize together, and how we tokenize it.
See its docstring for more information.

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

## Tokenization

wordfreq uses the Python package `regex`, which is a more advanced
implementation of regular expressions than the standard library, to
separate text into tokens that can be counted consistently. `regex`
produces tokens that follow the recommendations in [Unicode
Annex #29, Text Segmentation][uax29], including the optional rule that
splits words between apostrophes and vowels.

There are exceptions where we change the tokenization to work better
with certain languages:

- In Arabic and Hebrew, it additionally normalizes ligatures and removes
  combining marks.

- In Japanese and Korean, instead of using the regex library, it uses the
  external library `mecab-python3`. This is an optional dependency of wordfreq,
  and compiling it requires the `libmecab-dev` system package to be installed.

- In Chinese, it uses the external Python library `jieba`, another optional
  dependency.

- While the @ sign is usually considered a symbol and not part of a word,
  wordfreq will allow a word to end with "@" or "@s". This is one way of
  writing gender-neutral words in Spanish and Portuguese.

[uax29]: http://unicode.org/reports/tr29/

When wordfreq's frequency lists are built in the first place, the words are
tokenized according to this function.

    >>> from wordfreq import tokenize
    >>> tokenize('l@s niñ@s', 'es')
    ['l@s', 'niñ@s']
    >>> zipf_frequency('l@s', 'es')
    3.03

Because tokenization in the real world is far from consistent, wordfreq will
also try to deal gracefully when you query it with texts that actually break
into multiple tokens:

    >>> zipf_frequency('New York', 'en')
    5.32
    >>> zipf_frequency('北京地铁', 'zh')  # "Beijing Subway"
    3.29

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
    3.3

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

Sometimes, it's convenient to pretend that the boundaries between languages
coincide with national borders, following the maxim that "a language is a
dialect with an army and a navy" (Max Weinreich). This gets complicated when the
linguistic situation and the political situation diverge. Moreover, some of our
data sources rely on language detection, which of course has no idea which
country the writer of the text belongs to.

So we've had to make some arbitrary decisions about how to represent the
fuzzier language boundaries, such as those within Chinese, Malay, and
Croatian/Bosnian/Serbian.

Smoothing over our arbitrary decisions is the fact that we use the `langcodes`
module to find the best match for a language code. If you ask for word
frequencies in `cmn-Hans` (the fully specific language code for Mandarin in
Simplified Chinese), you will get the `zh` wordlist, for example.

## Additional CJK installation

Chinese, Japanese, and Korean have additional external dependencies so that
they can be tokenized correctly. They can all be installed at once by requesting
the 'cjk' feature:

    pip install wordfreq[cjk]

You can put `wordfreq[cjk]` in a list of dependencies, such as the
`[tool.poetry.dependencies]` list of your own project.

Tokenizing Chinese depends on the `jieba` package, tokenizing Japanese depends
on `mecab-python3` and `ipadic`, and tokenizing Korean depends on `mecab-python3`
and `mecab-ko-dic`.

As of version 2.4.2, you no longer have to install dictionaries separately.

## License

`wordfreq` is freely redistributable under the MIT license (see
`MIT-LICENSE.txt`), and it includes data files that may be
redistributed under a Creative Commons Attribution-ShareAlike 4.0
license (<https://creativecommons.org/licenses/by-sa/4.0/>).

`wordfreq` contains data extracted from Google Books Ngrams
(<http://books.google.com/ngrams>) and Google Books Syntactic Ngrams
(<http://commondatastorage.googleapis.com/books/syntactic-ngrams/index.html>).
The terms of use of this data are:

    Ngram Viewer graphs and data may be freely used for any purpose, although
    acknowledgement of Google Books Ngram Viewer as the source, and inclusion
    of a link to http://books.google.com/ngrams, would be appreciated.

`wordfreq` also contains data derived from the following Creative Commons-licensed
sources:

- The Leeds Internet Corpus, from the University of Leeds Centre for Translation
  Studies (<http://corpus.leeds.ac.uk/list.html>)

- Wikipedia, the free encyclopedia (<http://www.wikipedia.org>)

- ParaCrawl, a multilingual Web crawl (<https://paracrawl.eu>)

It contains data from OPUS OpenSubtitles 2018
(<http://opus.nlpl.eu/OpenSubtitles.php>), whose data originates from the
OpenSubtitles project (<http://www.opensubtitles.org/>) and may be used with
attribution to OpenSubtitles.

It contains data from various SUBTLEX word lists: SUBTLEX-US, SUBTLEX-UK,
SUBTLEX-CH, SUBTLEX-DE, and SUBTLEX-NL, created by Marc Brysbaert et al.
(see citations below) and available at
<http://crr.ugent.be/programs-data/subtitle-frequencies>.

I (Robyn Speer) have obtained permission by e-mail from Marc Brysbaert to
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

> Robyn Speer, Joshua Chin, Andrew Lin, Sara Jewett, & Lance Nathan.
> (2018, October 3). LuminosoInsight/wordfreq: v2.2. Zenodo.
> <https://doi.org/10.5281/zenodo.1443582>

The same citation in BibTex format:

```
@misc{robyn_speer_2018_1443582,
  author       = {Robyn Speer and
                  Joshua Chin and
                  Andrew Lin and
                  Sara Jewett and
                  Lance Nathan},
  title        = {LuminosoInsight/wordfreq: v2.2},
  month        = oct,
  year         = 2018,
  doi          = {10.5281/zenodo.1443582},
  url          = {https://doi.org/10.5281/zenodo.1443582}
}
```

## Citations to work that wordfreq is built on

- Bojar, O., Chatterjee, R., Federmann, C., Haddow, B., Huck, M., Hokamp, C.,
  Koehn, P., Logacheva, V., Monz, C., Negri, M., Post, M., Scarton, C.,
  Specia, L., & Turchi, M. (2015). Findings of the 2015 Workshop on Statistical
  Machine Translation.
  <http://www.statmt.org/wmt15/results.html>

- Brysbaert, M. & New, B. (2009). Moving beyond Kucera and Francis: A Critical
  Evaluation of Current Word Frequency Norms and the Introduction of a New and
  Improved Word Frequency Measure for American English. Behavior Research
  Methods, 41 (4), 977-990.
  <http://sites.google.com/site/borisnew/pub/BrysbaertNew2009.pdf>

- Brysbaert, M., Buchmeier, M., Conrad, M., Jacobs, A.M., Bölte, J., & Böhl, A.
  (2011). The word frequency effect: A review of recent developments and
  implications for the choice of frequency estimates in German. Experimental
  Psychology, 58, 412-424.

- Cai, Q., & Brysbaert, M. (2010). SUBTLEX-CH: Chinese word and character
  frequencies based on film subtitles. PLoS One, 5(6), e10729.
  <http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0010729>

- Davis, M. (2012). Unicode text segmentation. Unicode Standard Annex, 29.
  <http://unicode.org/reports/tr29/>

- Halácsy, P., Kornai, A., Németh, L., Rung, A., Szakadát, I., & Trón, V.
  (2004). Creating open language resources for Hungarian. In Proceedings of the
  4th international conference on Language Resources and Evaluation (LREC2004).
  <http://mokk.bme.hu/resources/webcorpus/>

- Keuleers, E., Brysbaert, M. & New, B. (2010). SUBTLEX-NL: A new frequency
  measure for Dutch words based on film subtitles. Behavior Research Methods,
  42(3), 643-650.
  <http://crr.ugent.be/papers/SUBTLEX-NL_BRM.pdf>

- Kudo, T. (2005). Mecab: Yet another part-of-speech and morphological
  analyzer.
  <http://mecab.sourceforge.net/>

- Lin, Y., Michel, J.-B., Aiden, E. L., Orwant, J., Brockman, W., and Petrov,
  S. (2012). Syntactic annotations for the Google Books Ngram Corpus.
  Proceedings of the ACL 2012 system demonstrations, 169-174.
  <http://aclweb.org/anthology/P12-3029>

- Lison, P. and Tiedemann, J. (2016). OpenSubtitles2016: Extracting Large
  Parallel Corpora from Movie and TV Subtitles. In Proceedings of the 10th
  International Conference on Language Resources and Evaluation (LREC 2016).
  <http://stp.lingfil.uu.se/~joerg/paper/opensubs2016.pdf>

- Ortiz Suárez, P. J., Sagot, B., and Romary, L. (2019). Asynchronous pipelines
  for processing huge corpora on medium to low resource infrastructures. In
  Proceedings of the Workshop on Challenges in the Management of Large Corpora
  (CMLC-7) 2019.
  <https://oscar-corpus.com/publication/2019/clmc7/asynchronous/>

- ParaCrawl (2018). Provision of Web-Scale Parallel Corpora for Official
  European Languages. <https://paracrawl.eu/>

- van Heuven, W. J., Mandera, P., Keuleers, E., & Brysbaert, M. (2014).
  SUBTLEX-UK: A new and improved word frequency database for British English.
  The Quarterly Journal of Experimental Psychology, 67(6), 1176-1190.
  <http://www.tandfonline.com/doi/pdf/10.1080/17470218.2013.850521>
