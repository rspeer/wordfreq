# This table comes from https://github.com/opendatakosovo/cyrillic-transliteration/blob/master/cyrtranslit/mapping.py,
# from the 'cyrtranslit' module, which is too flaky for us to just import.
SR_CYRL_TO_LATN_DICT = {
    ord('А'): 'A',   ord('а'): 'a',
    ord('Б'): 'B',   ord('б'): 'b',
    ord('В'): 'V',   ord('в'): 'v',
    ord('Г'): 'G',   ord('г'): 'g',
    ord('Д'): 'D',   ord('д'): 'd',
    ord('Ђ'): 'Đ',   ord('ђ'): 'đ',
    ord('Е'): 'E',   ord('е'): 'e',
    ord('Ж'): 'Ž',   ord('ж'): 'ž',
    ord('З'): 'Z',   ord('з'): 'z',
    ord('И'): 'I',   ord('и'): 'i',
    ord('Ј'): 'J',   ord('ј'): 'j',
    ord('К'): 'K',   ord('к'): 'k',
    ord('Л'): 'L',   ord('л'): 'l',
    ord('Љ'): 'Lj',  ord('љ'): 'lj',
    ord('М'): 'M',   ord('м'): 'm',
    ord('Н'): 'N',   ord('н'): 'n',
    ord('Њ'): 'Nj',  ord('њ'): 'nj',
    ord('О'): 'O',   ord('о'): 'o',
    ord('П'): 'P',   ord('п'): 'p',
    ord('Р'): 'R',   ord('р'): 'r',
    ord('С'): 'S',   ord('с'): 's',
    ord('Т'): 'T',   ord('т'): 't',
    ord('Ћ'): 'Ć',   ord('ћ'): 'ć',
    ord('У'): 'U',   ord('у'): 'u',
    ord('Ф'): 'F',   ord('ф'): 'f',
    ord('Х'): 'H',   ord('х'): 'h',
    ord('Ц'): 'C',   ord('ц'): 'c',
    ord('Ч'): 'Č',   ord('ч'): 'č',
    ord('Џ'): 'Dž',  ord('џ'): 'dž',
    ord('Ш'): 'Š',   ord('ш'): 'š',
}


def serbian_cyrillic_to_latin(text):
    return text.translate(SR_CYRL_TO_LATN_DICT)

