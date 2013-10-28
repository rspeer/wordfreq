SCHEMA = """
CREATE TABLE IF NOT EXISTS words (
    wordlist text,
    lang text,
    word text,
    freq real
)
"""

INDICES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS words_uniq ON words (wordlist, lang, word)",
    "CREATE INDEX IF NOT EXISTS words_by_freq ON words (wordlist, lang, freq DESC)",
]
