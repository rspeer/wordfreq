from .preprocess import MULTI_DIGIT_RE

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
#
# YEAR_LOG_PEAK is chosen by experimentation to make this probability add up to about
# .994. Here, that represents P(token represents a year) | P(token is 4 digits).
# The other .006 represents P(token does not represent a year) | P(token is 4 digits).

YEAR_LOG_PEAK = -1.875
NOT_YEAR_PROB = 0.006
REFERENCE_YEAR = 2019
PLATEAU_WIDTH = 20


def benford_freq(text: str) -> float:
    first_digit = int(text[0])
    return DIGIT_FREQS[first_digit] / 10 ** (len(text) - 1)


def year_freq(text: str) -> float:
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
    freq = 1.0
    for match in MULTI_DIGIT_RE.findall(text):
        if len(match) == 4:
            freq *= year_freq(match)
        else:
            freq *= benford_freq(match)
    return freq


print(sum(digit_freq("%04d" % year) for year in range(0, 10000)))
