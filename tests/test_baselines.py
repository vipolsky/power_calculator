import unittest
from unittest.mock import patch
from pandas.util.testing import assert_frame_equal
import pandas as pd
from ab_testing import baselines

class TestBaselines(unittest.TestCase):
    srd = baselines.simulate_rate_diff(sample_def = None, success_def = None)
    srd.sample_est = 10
    srd.success_est = 3
    df = pd.DataFrame({'success':[1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0] })
    
    def test_simulate_data(self):
        actual_df = self.srd.simulate_data(days = 2)
        expected_df = self.df 
        assert_frame_equal(actual_df, expected_df) 

    def test_get_rate_diff(self):
        diff = self.srd.get_rate_diff(df = self.df, split = 0.5, random_state = 1)
        self.assertEqual(diff, 0.2)

    def test_simulate_sampling_static(self):
        with patch('ab_testing.baselines.simulate_rate_diff.get_rate_diff', return_value = 0.2) as mock_rate_diff:
            max_diff, median_diff = self.srd.simulate_sampling(split = 0.5, df = self.df)
            self.assertEqual(round(max_diff,6), 0.2)
            self.assertEqual(round(median_diff, 6), 0.2)

    def test_simulate_sampling_dynamic(self):
        max_diff, median_diff = self.srd.simulate_sampling(split = 0.5, df = self.df)
        self.assertGreaterEqual(max_diff, median_diff)
        self.assertGreaterEqual(median_diff, 0)
        self.assertLessEqual(max_diff,1)
    
        
