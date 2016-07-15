import os

CONFIG = {
    # data_dir is a relative or absolute path to where the wordlist data
    # is stored
    'data_dir': 'data',
    'sources': {
        # A list of language codes that we'll look up in filenames for these
        # various data sources.
        #
        # Consider adding:
        # 'th' when we get tokenization for it
        # 'tl' with one more data source
        'twitter': [
            'ar', 'ca', 'de', 'el', 'en', 'es', 'fr', 'he', 'hi', 'id', 'it',
            'ja', 'ko', 'ms', 'nl', 'pl', 'pt', 'ru', 'sv', 'tr'
        ],
        # Languages with large Wikipedias. (Languages whose Wikipedia dump is
        # at least 200 MB of .xml.bz2 are included. Some widely-spoken
        # languages with 100 MB are also included, specifically Malay and
        # Hindi.)
        'wikipedia': [
            'ar', 'ca', 'de', 'el', 'en', 'es', 'fr', 'he', 'hi', 'id', 'it',
            'ja', 'ko', 'ms', 'nb', 'nl', 'pl', 'pt', 'ru', 'sv', 'tr',
            'bg', 'da', 'fi', 'hu', 'ro', 'uk'
        ],
        'opensubtitles': [
            # This list includes languages where the most common word in
            # OpenSubtitles appears at least 5000 times. However, we exclude
            # languages where SUBTLEX has apparently done a better job,
            # specifically German and Chinese.
            'ar', 'bg', 'bs', 'ca', 'cs', 'da', 'el', 'en', 'es', 'et',
            'fa', 'fi', 'fr', 'he', 'hr', 'hu', 'id', 'is', 'it', 'lt', 'lv',
            'mk', 'ms', 'nb', 'nl', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sq',
            'sr', 'sv', 'tr', 'uk'
        ],
        'leeds': [
            'ar', 'de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'pt', 'ru', 'zh'
        ],
        'google-books': [
            'en',
            # Using the 2012 data, we could get French, German, Italian,
            # Russian, Spanish, and (Simplified) Chinese.
        ],
        'subtlex-en': ['en'],
        'subtlex-other': ['de', 'nl', 'zh'],
        'jieba': ['zh'],

        # About 99.2% of Reddit is in English. There are pockets of
        # conversation in other languages, some of which may not be
        # representative enough for learning general word frequencies.
        #
        # However, there seem to be Spanish subreddits that are general enough
        # (including /r/es and /r/mexico).
        'reddit': ['en', 'es'],

        # Well-represented languages in the Common Crawl
        'commoncrawl': [
            'ar', 'bg', 'cs', 'da', 'de', 'el', 'es', 'fa', 'fi', 'fr',
            'he', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'ms', 'nb', 'nl',
            'pl', 'pt', 'ro', 'ru', 'sk', 'sv', 'ta', 'tr', 'uk', 'vi', 'zh'
        ],
    },
    # Subtlex languages that need to be pre-processed
    'wordlist_paths': {
        'twitter': 'generated/twitter/tweets-2014.{lang}.{ext}',
        'wikipedia': 'generated/wikipedia/wikipedia_{lang}.{ext}',
        'opensubtitles': 'generated/opensubtitles/opensubtitles_{lang}.{ext}',
        'leeds': 'generated/leeds/leeds_internet_{lang}.{ext}',
        'google-books': 'generated/google-books/google_books_{lang}.{ext}',
        'commoncrawl': 'generated/commoncrawl/commoncrawl_{lang}.{ext}',
        'subtlex-en': 'generated/subtlex/subtlex_{lang}.{ext}',
        'subtlex-other': 'generated/subtlex/subtlex_{lang}.{ext}',
        'jieba': 'generated/jieba/jieba_{lang}.{ext}',
        'reddit': 'generated/reddit/reddit_{lang}.{ext}',
        'combined': 'generated/combined/combined_{lang}.{ext}',
        'combined-dist': 'dist/combined_{lang}.{ext}',
        'combined-dist-large': 'dist/large_{lang}.{ext}',
        'twitter-dist': 'dist/twitter_{lang}.{ext}',
        'jieba-dist': 'dist/jieba_{lang}.{ext}'
    },
    'min_sources': 3,
    'big-lists': ['en', 'fr', 'es', 'pt', 'de', 'ar', 'el', 'it', 'ru'],
    # When dealing with language tags that come straight from cld2, we need
    # to un-standardize a few of them
    'cld2-language-aliases': {
        'nb': 'no',
        'he': 'iw',
        'jw': 'jv'
    }
}


def data_filename(filename):
    """
    Convert a relative filename to a path inside the configured data_dir.
    """
    return os.path.join(CONFIG['data_dir'], filename)


def wordlist_filename(source, language, extension='txt'):
    """
    Get the path where a particular built wordlist should go, parameterized by
    its language and its file extension.
    """
    path = CONFIG['wordlist_paths'][source].format(
        lang=language, ext=extension
    )
    return data_filename(path)


def source_names(language):
    """
    Get the names of data sources that supply data for the given language.
    """
    return sorted(key for key in CONFIG['sources']
                  if language in CONFIG['sources'][key])


def all_languages():
    """
    Get all languages that should have their data built, which is those that
    are supported by at least `min_sources` sources.
    """
    languages = set()
    for langlist in CONFIG['sources'].values():
        languages |= set(langlist)
    return [lang for lang in sorted(languages)
            if len(source_names(lang)) >= CONFIG['min_sources']]
