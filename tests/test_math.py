from nose.tools import assert_less_equal, assert_almost_equal
from wordfreq import half_harmonic_mean
from functools import reduce
import random


def check_hm_properties(inputs):
    # I asserted that the half-harmonic-mean formula is associative,
    # commutative, monotonic, and less than or equal to its inputs.
    # (Less if its inputs are strictly positive, in fact.)
    #
    # So let's test that what I said is true.
    hm1 = reduce(half_harmonic_mean, inputs)
    random.shuffle(inputs)
    hm2 = reduce(half_harmonic_mean, inputs)
    assert_almost_equal(hm1, hm2)

    inputs[0] *= 2
    hm3 = reduce(half_harmonic_mean, inputs)
    assert_less_equal(hm2, hm3)


def test_half_harmonic_mean():
    for count in range(2, 6):
        for rep in range(10):
            # get some strictly positive arbitrary numbers
            inputs = [random.expovariate(0.01)
                      for i in range(count)]
            yield check_hm_properties, inputs

