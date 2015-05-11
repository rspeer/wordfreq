import os

CONFIG = {
    'version': '0.9.0',
    # data_dir is a relative or absolute path to where the wordlist data
    # is stored
    'data_dir': 'data',
    'sources': {
        # A list of language codes (possibly un-standardized) that we'll
        # look up in filenames for these various data sources.
        'twitter': [
            'ar', 'de', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'nl',
            'pt', 'ru',
            # can be added later: 'th', 'tr'
        ],
        'wikipedia': [
            'ar', 'de', 'en', 'es', 'fr', 'id', 'it', 'ja', 'ko', 'ms', 'nl',
            'pt', 'ru'
            # many more can be added
        ],
        'opensubtitles': [
            # All languages where the most common word in OpenSubtitles
            # appears at least 5000 times
            'ar', 'bg', 'bs', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et',
            'fa', 'fi', 'fr', 'he', 'hr', 'hu', 'id', 'is', 'it', 'lt', 'lv',
            'mk', 'ms', 'nb', 'nl', 'pl', 'pt', 'ro', 'sk', 'sl', 'sq', 'sr',
            'sv', 'tr', 'uk', 'zh'
        ],
        'leeds': [
            'ar', 'de', 'el', 'en', 'es', 'fr', 'it', 'ja', 'pt', 'ru', 'zh'
        ],
        'google-books': [
            'en',
            # Using the 2012 data, we could get French, German, Italian,
            # Russian, Spanish, and (Simplified) Chinese.
        ]
    },
    'wordlist_paths': {
        'twitter': 'generated/twitter/tweets-2014.{lang}.{ext}',
        'wikipedia': 'generated/wikipedia/wikipedia_{lang}.{ext}',
        'opensubtitles': 'generated/opensubtitles/opensubtitles_{lang}.{ext}',
        'leeds': 'generated/leeds/leeds_internet_{lang}.{ext}',
        'google-books': 'generated/google-books/google_books_{lang}.{ext}',
        'combined': 'generated/combined/combined_{lang}.{ext}'
    },
    'min_sources': 2
}


def data_filename(filename):
    return os.path.join(CONFIG['data_dir'], filename)


def wordlist_filename(source, language, extension='txt'):
    path = CONFIG['wordlist_paths'][source].format(
        lang=language, ext=extension
    )
    return data_filename(path)


def source_names(language):
    """
    Get the names of data sources that supply data for the given language.
    """
    return sorted([key for key in CONFIG['sources']
                  if language in CONFIG['sources'][key]])


def all_languages():
    languages = set()
    for langlist in CONFIG['sources'].values():
        languages |= set(langlist)
    return [lang for lang in sorted(languages)
            if len(source_names(lang))
            >= CONFIG['min_sources']]

