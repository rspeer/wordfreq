import os

CONFIG = {
    'version': '0.9.0',
    # data_dir is a relative or absolute path to where the wordlist data
    # is stored
    'data_dir': 'data',
    'languages': [
        'en', 'es', 'fr', 'de', 'pt', 'nl', 'ru', 'it', 'ar', 'ms', 'id',
        'ja', 'ko', 'zh-Hans', 'zh-Hant',
    ],
    # Skip the Chinese Wikipedia until we know what to do with it
    'wp_languages': [
        'en', 'es', 'fr', 'de', 'pt', 'nl', 'ru', 'it', 'ar', 'ms', 'id',
        'ja', 'ko'
    ]
}


def data_filename(filename):
    return os.path.join(CONFIG['data_dir'], filename)
