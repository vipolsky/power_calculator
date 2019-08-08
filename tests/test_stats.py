import unittest
import logging
from ab_testing import stats


logging.disable(logging.CRITICAL)


class TestPower(unittest.TestCase):

    def test_calc_power(self):
        nip = stats.non_inferiority(delta = -.005, pA = 0.303, pB = 0.30, kappa = 1, nB = 50000, samples_per_day = 5000)
        actual = round(nip.calc_power(), 3)
        expected = .867
        self.assertEqual(actual, expected)

    def test_calc_samples(self):
        nip = stats.non_inferiority(delta = -.005, pA = 0.303, pB = 0.30, kappa = 1, power = 0.8, samples_per_day = 5000)
        actual = nip.calc_samples()
        expected = 40639
        self.assertLess(abs(actual-expected), 100)
