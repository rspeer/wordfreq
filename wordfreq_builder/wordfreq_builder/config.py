import os

CONFIG = {
    'version': '0.8',
    'data_dir': './data',
    'languages': [
        'en', 'es', 'fr', 'de', 'pt', 'nl', 'ru', 'it', 'ar', 'ms', 'id',
        'ja', 'ko', 'zh-Hans', 'zh-Hant',
    ]
}


def data_filename(filename):
    return os.path.join(CONFIG['data_dir'], filename)
