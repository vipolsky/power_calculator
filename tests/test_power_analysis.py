import unittest
from unittest.mock import patch
import logging
from ab_testing.power_analysis import non_inferiority_power_analysis, superiority_power_analysis


logging.disable(logging.CRITICAL)


class TestPower(unittest.TestCase):

    @patch.object(non_inferiority_power_analysis, 'fetch_successes_and_samples')
    def test_init_delta_non_inferiority(self, mock_successes_and_samples):
        mock_successes_and_samples.return_value = (3000, 2000)
        #positive deltas are made negative for non-inferiority
        ni_pos = non_inferiority_power_analysis(split = [.5, .5], metric = 'need_to_book_lagged', lag = 7, days = 30, delta = .003)
        self.assertEqual(ni_pos.delta, -.003)
        #negative deltas remain made negative for non-inferiority
        ni_neg = non_inferiority_power_analysis(split = [.5, .5], metric = 'need_to_book_lagged', lag = 7, days = 30, delta = -.003)
        self.assertEqual(ni_neg.delta, -.003)

    @patch.object(non_inferiority_power_analysis, 'fetch_successes_and_samples')
    def test_calculate_expected_delta_non_inferiority(self, mock_successes_and_samples):
        mock_successes_and_samples.return_value = (6000, 4000)
        ni = non_inferiority_power_analysis(split = [.5,.5], metric = 'need_to_book_lagged', lag = 7, days = 30)
        self.assertEqual(round(ni.delta, 4) , -0.0063)

       # def test_power_calculation_non_inferiority(self):
       #     with patch.object(non_inferiority_power_analysis, 'fetch_successes_and_samples', return_value=(6000, 4000)) as mock_method:
       #         ni_50_50 = non_inferiority_power_analysis(split = [.5,.5], metric = 'need_to_book_lagged', lag = 7, days = 30, delta = -.005)
       #         self.assertLessEqual(abs(ni_50_50.calculate_power()-0.6991), .05)



