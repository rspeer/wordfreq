from wordfreq import lossy_tokenize, tokenize, word_frequency


def test_gender_neutral_at():
    # Recognize the gender-neutral @ in Spanish as part of the word
    text = "La protección de los derechos de tod@s l@s trabajador@s migrantes"
    assert tokenize(text, "es") == [
        "la",
        "protección",
        "de",
        "los",
        "derechos",
        "de",
        "tod@s",
        "l@s",
        "trabajador@s",
        "migrantes",
    ]

    text = "el distrito 22@ de Barcelona"
    assert tokenize(text, "es") == ["el", "distrito", "22@", "de", "barcelona"]
    assert lossy_tokenize(text, "es") == ["el", "distrito", "22@", "de", "barcelona"]

    # It also appears in Portuguese
    text = "direitos e deveres para @s membr@s da comunidade virtual"
    assert tokenize(text, "pt") == [
        "direitos",
        "e",
        "deveres",
        "para",
        "@s",
        "membr@s",
        "da",
        "comunidade",
        "virtual",
    ]

    # Because this is part of our tokenization, the language code doesn't
    # actually matter, as long as it's a language with Unicode tokenization
    text = "@s membr@s da comunidade virtual"
    assert tokenize(text, "en") == ["@s", "membr@s", "da", "comunidade", "virtual"]


def test_at_in_corpus():
    # We have a word frequency for "l@s"
    assert word_frequency("l@s", "es") > 0

    # It's not just treated as a word break
    assert word_frequency("l@s", "es") < word_frequency("l s", "es")


def test_punctuation_at():
    # If the @ appears alone in a word, we consider it to be punctuation
    text = "operadores de canal, que são aqueles que têm um @ ao lado do nick"
    assert tokenize(text, "pt") == [
        "operadores",
        "de",
        "canal",
        "que",
        "são",
        "aqueles",
        "que",
        "têm",
        "um",
        "ao",
        "lado",
        "do",
        "nick",
    ]

    assert tokenize(text, "pt", include_punctuation=True) == [
        "operadores",
        "de",
        "canal",
        ",",
        "que",
        "são",
        "aqueles",
        "que",
        "têm",
        "um",
        "@",
        "ao",
        "lado",
        "do",
        "nick",
    ]

    # If the @ is not at the end of the word or part of the word ending '@s',
    # it is also punctuation
    text = "un archivo hosts.deny que contiene la línea ALL:ALL@ALL"
    assert tokenize(text, "es") == [
        "un",
        "archivo",
        "hosts.deny",
        "que",
        "contiene",
        "la",
        "línea",
        "all:all",
        "all",
    ]

    # Make sure not to catch e-mail addresses
    text = "info@something.example"
    assert tokenize(text, "en") == ["info", "something.example"]
