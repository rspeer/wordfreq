# wordfreq\_builder

This package builds the data files for [wordfreq](https://github.com/LuminosoInsight/wordfreq).

It requires a fair amount of external input data (42 GB of it, as of this
writing), which is unfortunately not version-controlled. We'd like to remedy
this situation using some sort of framework, but this requires sorting things
out with Tools.

## How to build it

- Set up your external hard disk, your networked file system, or whatever thing
  you have that's got a couple hundred GB of space free. Let's suppose the
  directory of it that you want to use is called `/ext/data`.

- Copy the input data:

    cp -rv /nfs/broadway/data/wordfreq_builder /ext/data/

- Make a symbolic link so that `data/` in this directory points to
  your copy of the input data:

    ln -s /ext/data/wordfreq_builder data

- Install the Ninja build system:

    sudo apt-get install ninja-build

- We need to build a Ninja build file using the Python code in
  `wordfreq_builder/ninja.py`. We could do this with Ninja, but... you see the
  chicken-and-egg problem, don't you. So this is the one thing the Makefile
  knows how to do.

    make

- Start the build, and find something else to do for a few hours:

    ninja -v

- You can copy the results into wordfreq with this command (supposing that
  $WORDFREQ points to your wordfreq repo):

    cp data/generated/combined/*.msgpack.gz $WORDFREQ/wordfreq/data/


## The dBpack data format

We pack the wordlists into a small amount of space using a format that I
call "dBpack". This is the data that's found in the .msgpack.gz files that
are output at the end. The format is as follows:

- The file on disk is a gzipped file in msgpack format, which decodes to a
  list of lists of words.

- Each inner list of words corresponds to a particular word frequency,
  rounded to the nearest decibel. 0 dB represents a word that occurs with
  probability 1, so it is the only word in the data (this of course doesn't
  happen). -20 dB represents a word that occurs once per 100 tokens, -30 dB
  represents a word that occurs once per 1000 tokens, and so on.

- The index of each list within the overall list is the negative of its
  frequency in decibels.

- Each inner list is sorted in alphabetical order.

As an example, consider a corpus consisting only of the words "red fish
blue fish". The word "fish" occurs as 50% of tokens (-3 dB), while "red"
and "blue" occur as 25% of tokens (-6 dB). The dBpack file of their word
frequencies would decode to this list:

    [[], [], [], ['fish'], [], [], ['blue', 'red']]


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

The original files are in `data/source-lists/leeds`, and they're processed
by the `convert_leeds` rule in `rules.ninja`.

### Twitter

The file `data/raw-input/twitter/all-2014.txt` contains about 72 million tweets
collected by the `ftfy.streamtester` package in 2014.

It takes a lot of work -- and a lot of Rosette, in particular -- to convert
these tweets into data that's usable for wordfreq. They have to be
language-detected and then tokenized. So the result of language-detection
and tokenization is stored in `data/intermediate/twitter`.

### Google Books

We use English word frequencies from [Google Books Syntactic Ngrams][gbsn].
We pretty much ignore the syntactic information, and only use this version
because it's cleaner. The data comes in the form of 99 gzipped text files in
`data/raw-input/google-books`.

[gbsn]: http://commondatastorage.googleapis.com/books/syntactic-ngrams/index.html

### OpenSubtitles

[Some guy](https://invokeit.wordpress.com/frequency-word-lists/) made word
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

