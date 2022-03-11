import regex

# Frequencies of leading digits, according to Benford's law, sort of.
# Benford's law doesn't describe numbers with leading zeroes, because "007"
# and "7" are the same number, but for us they should have different frequencies.
# I added an estimate for the frequency of numbers with leading zeroes.
DIGIT_FREQS = [0.009, 0.300, 0.175, 0.124, 0.096, 0.078, 0.066, 0.057, 0.050, 0.045]

# Suppose you have a token NNNN, a 4-digit number representing a year. We're making
# a probability distribution of P(token=NNNN) | P(token is 4 digits).
#
# We do this with a piecewise exponential function whose peak is a plateau covering
# the years 2019 to 2039.

# Determined by experimentation: makes the probabilities of all years add up to 90%.
# The other 10% goes to NOT_YEAR_PROB. tests/test_numbers.py confirms that this
# probability distribution adds up to 1.
YEAR_LOG_PEAK = -1.9185
NOT_YEAR_PROB = 0.1
REFERENCE_YEAR = 2019
PLATEAU_WIDTH = 20

DIGIT_RE = regex.compile(r"\d")
MULTI_DIGIT_RE = regex.compile(r"\d[\d.,]+")
PURE_DIGIT_RE = regex.compile(r"\d+")


def benford_freq(text: str) -> float:
    """
    Estimate the frequency of a digit sequence according to Benford's law.
    """
    first_digit = int(text[0])
    return DIGIT_FREQS[first_digit] / 10 ** (len(text) - 1)


def year_freq(text: str) -> float:
    """
    Estimate the relative frequency of a particular 4-digit sequence representing
    a year.

    For example, suppose text == "1985". We're estimating the probability that a
    randomly-selected token from a large corpus will be "1985" and refer to the
    year, _given_ that it is 4 digits. Tokens that are not 4 digits are not involved
    in the probability distribution.
    """
    year = int(text)

    # Fitting a line to the curve seen at
    # https://twitter.com/r_speer/status/1493715982887571456.

    if year <= REFERENCE_YEAR:
        year_log_freq = YEAR_LOG_PEAK - 0.0083 * (REFERENCE_YEAR - year)

    # It's no longer 2019, which is when the Google Books data was last collected.
    # It's 2022 as I write this, and possibly even later as you're using it. Years
    # keep happening.
    #
    # So, we'll just keep the expected frequency of the "present" year constant for
    # 20 years.

    elif REFERENCE_YEAR < year <= REFERENCE_YEAR + PLATEAU_WIDTH:
        year_log_freq = YEAR_LOG_PEAK

    # Fall off quickly to catch up with the actual frequency of future years
    # (it's low). This curve is made up to fit with the made-up "present" data above.
    else:
        year_log_freq = YEAR_LOG_PEAK - 0.2 * (year - (REFERENCE_YEAR + PLATEAU_WIDTH))

    year_prob = 10.0**year_log_freq

    # If this token _doesn't_ represent a year, then use the Benford frequency
    # distribution.
    not_year_prob = NOT_YEAR_PROB * benford_freq(text)
    return year_prob + not_year_prob


def digit_freq(text: str) -> float:
    """
    Get the relative frequency of a string of digits, using our estimates.
    """
    freq = 1.0
    for match in MULTI_DIGIT_RE.findall(text):
        for submatch in PURE_DIGIT_RE.findall(match):
            if len(submatch) == 4:
                freq *= year_freq(submatch)
            else:
                freq *= benford_freq(submatch)
    return freq


def has_digit_sequence(text: str) -> bool:
    """
    Returns True iff the text has a digit sequence that will be normalized out
    and handled with `digit_freq`.
    """
    return bool(MULTI_DIGIT_RE.match(text))


def _sub_zeroes(match: regex.Match) -> str:
    """
    Given a regex match, return what it matched with digits replaced by
    zeroes.
    """
    return DIGIT_RE.sub("0", match.group(0))


def smash_numbers(text: str) -> str:
    """
    Replace sequences of multiple digits with zeroes, so we don't need to
    distinguish the frequencies of thousands of numbers.
    """
    return MULTI_DIGIT_RE.sub(_sub_zeroes, text)
