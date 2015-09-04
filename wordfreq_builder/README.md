# wordfreq\_builder

This package builds the data files for [wordfreq](https://github.com/LuminosoInsight/wordfreq).

It requires a fair amount of external input data (42 GB of it, as of this
writing), which unfortunately we don't have a plan for how to distribute
outside of Luminoso yet.

The data can be publicly obtained in various ways, so here we'll at least
document where it comes from. We hope to come up with a process that's more
reproducible eventually.

The good news is that you don't need to be able to run this process to use
wordfreq. The built results are already in the `wordfreq/data` directory.

## How to build it

Set up your external hard disk, your networked file system, or whatever thing
you have that's got a couple hundred GB of space free. Let's suppose the
directory of it that you want to use is called `/ext/data`.

Get the input data. At Luminoso, this is available in the directory
`/nfs/broadway/data/wordfreq_builder`. The sections below explain where the
data comes from.

Copy the input data:

    cp -rv /nfs/broadway/data/wordfreq_builder /ext/data/

Make a symbolic link so that `data/` in this directory points to
your copy of the input data:

    ln -s /ext/data/wordfreq_builder data

Install the Ninja build system:

    sudo apt-get install ninja-build

We need to build a Ninja build file using the Python code in
`wordfreq_builder/ninja.py`. We could do this with Ninja, but... you see the
chicken-and-egg problem, don't you. So this is the one thing the Makefile
knows how to do.

    make

Start the build, and find something else to do for a few hours:

    ninja -v

You can copy the results into wordfreq with this command:

    cp data/dist/*.msgpack.gz ../wordfreq/data/


## The Ninja build process

Ninja is a lot like Make, except with one big {drawback|advantage}: instead of
writing bizarre expressions in an idiosyncratic language to let Make calculate
which files depend on which other files...

...you just tell Ninja which files depend on which other files.

The Ninja documentation suggests using your favorite scripting language to
create the dependency list, so that's what we've done in `ninja.py`.

Dependencies in Ninja refer to build rules. These do need to be written by hand
in Ninja's own format, but the task is simpler. In this project, the build
rules are defined in `rules.ninja`. They'll be concatenated with the
Python-generated dependency definitions to form the complete build file,
`build.ninja`, which is the default file that Ninja looks at when you run
`ninja`.

So a lot of the interesting work in this package is done in `rules.ninja`.
This file defines shorthand names for long commands. As a simple example,
the rule named `format_twitter` applies the command

    python -m wordfreq_builder.cli.format_twitter $in $out

to the dependency file `$in` and the output file `$out`.

The specific rules are described by the comments in `rules.ninja`.

## Data sources

### Leeds Internet Corpus

Also known as the "Web as Corpus" project, this is a University of Leeds
project that collected wordlists in assorted languages by crawling the Web.
The results are messy, but they're something. We've been using them for quite
a while.

These files can be downloaded from the [Leeds corpus page][leeds].

The original files are in `data/source-lists/leeds`, and they're processed
by the `convert_leeds` rule in `rules.ninja`.

[leeds]: http://corpus.leeds.ac.uk/list.html

### Twitter

The file `data/raw-input/twitter/all-2014.txt` contains about 72 million tweets
collected by the `ftfy.streamtester` package in 2014.

We are not allowed to distribute the text of tweets. However, this process could
be reproduced by running `ftfy.streamtester`, part of the [ftfy][] package, for
a couple of weeks.

[ftfy]: https://github.com/LuminosoInsight/python-ftfy

### Google Books

We use English word frequencies from [Google Books Syntactic Ngrams][gbsn].
We pretty much ignore the syntactic information, and only use this version
because it's cleaner. The data comes in the form of 99 gzipped text files in
`data/raw-input/google-books`.

[gbsn]: http://commondatastorage.googleapis.com/books/syntactic-ngrams/index.html

### Wikipedia

Another source we use is the full text of Wikipedia in various languages. This
text can be difficult to extract efficiently, and for this purpose we use a
custom tool written in Nim 0.11, called [wiki2text][]. To build the Wikipedia
data, you need to separately install Nim and wiki2text.

The input data files are the XML dumps that can be found on the [Wikimedia
backup index][wikidumps]. For example, to get the latest Spanish data, go to
https://dumps.wikimedia.org/frwiki/latest and look for the filename of the form
`*.pages-articles.xml.bz2`. If this file isn't there, look for an older dump
where it is. You'll need to download such a file for each language that's
configured for Wikipedia in `wordfreq_builder/config.py`.

[wiki2text]: https://github.com/rspeer/wiki2text
[wikidumps]: https://dumps.wikimedia.org/backup-index.html

### OpenSubtitles

[Hermit Dave](https://invokeit.wordpress.com/frequency-word-lists/) made word
frequency lists out of the subtitle text on OpenSubtitles. This data was
used to make Wiktionary word frequency lists at one point, but it's been
updated significantly since the version Wiktionary got.

The wordlists are in `data/source-lists/opensubtitles`.

In order to fit into the wordfreq pipeline, we renamed lists with different variants
of the same language code, to distinguish them fully according to BCP 47. Then we
concatenated the different variants into a single list, as follows:

* `zh_tw.txt` was renamed to `zh-Hant.txt`
* `zh_cn.txt` was renamed to `zh-Hans.txt`
* `zh.txt` was renamed to `zh-Hani.txt`
* `zh-Hant.txt`, `zh-Hans.txt`, and `zh-Hani.txt` were concatenated into `zh.txt`
* `pt.txt` was renamed to `pt-PT.txt`
* `pt_br.txt` was renamed to `pt-BR.txt`
* `pt-BR.txt` and `pt-PT.txt` were concatenated into `pt.txt`

We also edited the English data to re-add "'t" to words that had obviously lost
it, such as "didn" in the place of "didn't". We applied this to words that
became much less common words in the process, which means this wordlist no
longer represents the words 'don' and 'won', as we assume most of their
frequency comes from "don't" and "won't". Words that turned into similarly
common words, however, were left alone: this list doesn't represent "can't"
because the word was left as "can".

### SUBTLEX

Mark Brysbaert gave us permission by e-mail to use the SUBTLEX word lists in
wordfreq and derived works without the "academic use" restriction, under the
following reasonable conditions:

- Wordfreq and code derived from it must credit the SUBTLEX authors.
  (See the citations in the top-level `README.md` file.)
- It must remain clear that SUBTLEX is freely available data.

`data/source-lists/subtlex` contains the following files:

- `subtlex.en-US.txt`, which was downloaded from [here][subtlex-us],
  extracted, and converted from ISO-8859-1 to UTF-8
- `subtlex.en-GB.txt`, which was exported as tab-separated UTF-8
  from [this Excel file][subtlex-uk]
- `subtlex.zh.txt`, which was downloaded and extracted from
  [here][subtlex-ch]

[subtlex-us]: http://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus/subtlexus5.zip
[subtlex-uk]: http://crr.ugent.be/papers/SUBTLEX-UK_all.xlsx
[subtlex-ch]: http://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch/subtlexch131210.zip

