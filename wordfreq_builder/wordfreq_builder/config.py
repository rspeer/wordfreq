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
        # 'hi' when we stop messing up its tokenization
        # 'tl' with one more data source
        'twitter': [
            'ar', 'de', 'el', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'nl',
            'pl', 'pt', 'ru', 'sv', 'tr'
        ],
        'wikipedia': [
            'ar', 'de', 'en', 'el', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'nl',
            'pl', 'pt', 'ru', 'sv', 'tr'
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

        # About 99.2% of Reddit is in English, but there are pockets of
        # conversation in other languages. These are the languages that seem
        # to have enough non-spam comments to actually learn from.
        'reddit': ['de', 'en', 'es', 'sv']
    },
    # Subtlex languages that need to be pre-processed
    'wordlist_paths': {
        'twitter': 'generated/twitter/tweets-2014.{lang}.{ext}',
        'wikipedia': 'generated/wikipedia/wikipedia_{lang}.{ext}',
        'opensubtitles': 'generated/opensubtitles/opensubtitles_{lang}.{ext}',
        'leeds': 'generated/leeds/leeds_internet_{lang}.{ext}',
        'google-books': 'generated/google-books/google_books_{lang}.{ext}',
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
    'min_sources': 2,
    'big-lists': ['en', 'fr', 'es', 'pt', 'de']
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
