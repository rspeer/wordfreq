from wordfreq import tokenize, word_frequency


def test_apostrophes():
    # Test that we handle apostrophes in French reasonably.
    assert tokenize("qu'un", "fr") == ["qu", "un"]
    assert tokenize("qu'un", "fr", include_punctuation=True) == ["qu'", "un"]
    assert tokenize("langues d'oïl", "fr") == ["langues", "d", "oïl"]
    assert tokenize("langues d'oïl", "fr", include_punctuation=True) == [
        "langues",
        "d'",
        "oïl",
    ]
    assert tokenize("l'heure", "fr") == ["l", "heure"]
    assert tokenize("l'ànima", "ca") == ["l", "ànima"]
    assert tokenize("l'anima", "it") == ["l", "anima"]
    assert tokenize("l'heure", "fr", include_punctuation=True) == ["l'", "heure"]
    assert tokenize("L'Hôpital", "fr", include_punctuation=True) == ["l'", "hôpital"]
    assert tokenize("aujourd'hui", "fr") == ["aujourd'hui"]
    assert tokenize("This isn't French", "en") == ["this", "isn't", "french"]

    # This next behavior is not ideal -- we would prefer "dell'" to be handled
    # the same as "l'" -- but this is the most consistent result we can get without
    # Italian-specific rules.
    #
    # Versions of regex from 2019 and earlier would give ['dell', 'anima'], which
    # is better but inconsistent.
    assert tokenize("dell'anima", "it") == ["dell'anima"]

    # Versions of regex from 2019 and earlier would give ['hawai', 'i'], and that's
    # an example of why we don't want the apostrophe-vowel fix to apply everywhere.
    assert tokenize("hawai'i", "en") == ["hawai'i"]


def test_catastrophes():
    # More apostrophes, but this time they're in Catalan, and there's other
    # mid-word punctuation going on too.
    assert tokenize("M'acabo d'instal·lar.", "ca") == ["m", "acabo", "d", "instal·lar"]
    assert tokenize("M'acabo d'instal·lar.", "ca", include_punctuation=True) == [
        "m'",
        "acabo",
        "d'",
        "instal·lar",
        ".",
    ]


def test_alternate_codes():
    # Try over-long language codes for French and Catalan
    assert tokenize("qu'un", "fra") == ["qu", "un"]
    assert tokenize("qu'un", "fre") == ["qu", "un"]
    assert tokenize("M'acabo d'instal·lar.", "cat") == ["m", "acabo", "d", "instal·lar"]
