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

