## Version 2.0.1 (2018-05-01)

Fixed edge cases that inserted spurious token boundaries when Japanese text is
run through `simple_tokenize`, because of a few characters that don't match any
of our "spaceless scripts".

It is not a typical situation for Japanese text to be passed through
`simple_tokenize`, because Japanese text should instead use the
Japanese-specific tokenization in `wordfreq.mecab`.

However, some downstream uses of wordfreq have justifiable reasons to pass all
terms through `simple_tokenize`, even terms that may be in Japanese, and in
those cases we want to detect only the most obvious token boundaries.

In this situation, we no longer try to detect script changes, such as between
kanji and katakana, as token boundaries. This particularly allows us to keep
together Japanese words where ヶ appears betwen kanji, as well as words that
use the iteration mark 々.

This change does not affect any word frequencies. (The Japanese word list uses
`wordfreq.mecab` for tokenization, not `simple_tokenize`.)



## Version 2.0 (2018-03-14)

The big change in this version is that text preprocessing, tokenization, and
postprocessing to look up words in a list are separate steps.

If all you need is preprocessing to make text more consistent, use
`wordfreq.preprocess.preprocess_text(text, lang)`. If you need preprocessing
and tokenization, use `wordfreq.tokenize(text, lang)` as before. If you need
all three steps, use the new function `wordfreq.lossy_tokenize(text, lang)`.

As a breaking change, this means that the `tokenize` function no longer has
the `combine_numbers` option, because that's a postprocessing step. For
the same behavior, use `lossy_tokenize`, which always combines numbers.

Similarly, `tokenize` will no longer replace Chinese characters with their
Simplified Chinese version, while `lossy_tokenize` will.

Other changes:

- There's a new default wordlist for each language, called "best". This
  chooses the "large" wordlist for that language, or if that list doesn't
  exist, it falls back on "small".

- The wordlist formerly named "combined" (this name made sense long ago)
  is now named "small". "combined" remains as a deprecated alias.

- The "twitter" wordlist has been removed. If you need to compare word
  frequencies from individual sources, you can work with the separate files in
  [exquisite-corpus][].

- Tokenizing Chinese will preserve the original characters, no matter whether
  they are Simplified or Traditional, instead of replacing them all with
  Simplified characters.

- Different languages require different processing steps, and the decisions
  about what these steps are now appear in the `wordfreq.language_info` module,
  replacing a bunch of scattered and inconsistent `if` statements.

- Tokenizing CJK languages while preserving punctuation now has a less confusing
  implementation.

- The preprocessing step can transliterate Azerbaijani, although we don't yet
  have wordlists in this language. This is similar to how the tokenizer
  supports many more languages than the ones with wordlists, making future
  wordlists possible.

- Speaking of that, the tokenizer will log a warning (once) if you ask to tokenize
  text written in a script we can't tokenize (such as Thai).

- New source data from [exquisite-corpus][] includes OPUS OpenSubtitles 2018.

Nitty gritty dependency changes:

- Updated the regex dependency to 2018.02.21. (We would love suggestions on
  how to coexist with other libraries that use other versions of `regex`,
  without a `>=` requirement that could introduce unexpected data-altering
  changes.)

- We now depend on `msgpack`, the new name for `msgpack-python`.

[exquisite-corpus]: https://github.com/LuminosoInsight/exquisite-corpus


## Version 1.7.0 (2017-08-25)

- Tokenization will always keep Unicode graphemes together, including
  complex emoji introduced in Unicode 10
- Update the Wikipedia source data to April 2017
- Remove some non-words, such as the Unicode replacement character and the
  pilcrow sign, from frequency lists
- Support Bengali and Macedonian, which passed the threshold of having enough
  source data to be included


## Version 1.6.1 (2017-05-10)

- Depend on langcodes 1.4, with a new language-matching system that does not
  depend on SQLite.

  This prevents silly conflicts where langcodes' SQLite connection was
  preventing langcodes from being used in threads.


## Version 1.6.0 (2017-01-05)

- Support Czech, Persian, Ukrainian, and Croatian/Bosnian/Serbian
- Add large lists in Chinese, Finnish, Japanese, and Polish
- Data is now collected and built using Exquisite Corpus
  (https://github.com/LuminosoInsight/exquisite-corpus)
- Add word frequencies from OPUS OpenSubtitles 2016
- Add word frequencies from the MOKK Hungarian Webcorpus
- Expand Google Books Ngrams data to cover 8 languages
- Expand language detection on Reddit to cover 13 languages with large enough
  Reddit communities
- Drop the Common Crawl; we have enough good sources now that we don't have
  to deal with all that spam
- Add automatic transliteration of Serbian text
- Adjust tokenization of apostrophes next to vowel sounds: the French word
  "l'heure" is now tokenized similarly to "l'arc"
- Multi-digit numbers of each length are smashed into the same word frequency,
  to remove meaningless differences and increase compatibility with word2vec.
  (Internally, their digits are replaced by zeroes.)
- Another new frequency-merging strategy (drop the highest and lowest,
  average the rest)


## Version 1.5.1 (2016-08-19)

- Bug fix: Made it possible to load the Japanese or Korean dictionary when the
  other one is not available


## Version 1.5.0 (2016-08-08)

- Include word frequencies learned from the Common Crawl
- Support Bulgarian, Catalan, Danish, Finnish, Hebrew, Hindi, Hungarian,
  Norwegian Bokmål, and Romanian
- Improve Korean with MeCab tokenization
- New frequency-merging strategy (weighted median)
- Include Wikipedia as a Chinese source (mostly Traditional)
- Include Reddit as a Spanish source
- Remove Greek Twitter because its data is poorly language-detected
- Add large lists in Arabic, Dutch, Italian
- Remove marks from more languages
- Deal with commas and cedillas in Turkish and Romanian
- Fix tokenization of Southeast and South Asian scripts
- Clean up Git history by removing unused large files

[Announcement blog post](https://blog.conceptnet.io/2016/08/22/wordfreq-1-5-more-data-more-languages-more-accuracy)


## Version 1.4 (2016-06-02)

- Add large lists in English, German, Spanish, French, and Portuguese
- Add `zipf_frequency` function

[Announcement blog post](https://blog.conceptnet.io/2016/06/02/wordfreq-1-4-more-words-plus-word-frequencies-from-reddit/)


## Version 1.3 (2016-01-14)

- Add Reddit comments as an English source


## Version 1.2 (2015-10-29)

- Add SUBTLEX data
- Better support for Chinese, using Jieba for tokenization, and mapping
  Traditional Chinese characters to Simplified
- Improve Greek
- Add Polish, Swedish, and Turkish
- Tokenizer can optionally preserve punctuation
- Detect when sources stripped "'t" off of English words, and repair their
  frequencies

[Announcement blog post](https://blog.luminoso.com/2015/10/29/wordfreq-1-2-is-better-at-chinese-english-greek-polish-swedish-and-turkish/)


## Version 1.1 (2015-08-25)

- Use the 'regex' package to implement Unicode tokenization that's mostly
  consistent across languages
- Use NFKC normalization in Japanese and Arabic


## Version 1.0 (2015-07-28)

- Create compact word frequency lists in English, Arabic, German, Spanish,
  French, Indonesian, Japanese, Malay, Dutch, Portuguese, and Russian
- Marginal support for Greek, Korean, Chinese
- Fresh start, dropping compatibility with wordfreq 0.x and its unreasonably
  large downloads

