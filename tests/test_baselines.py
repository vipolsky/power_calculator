import unittest
from unittest.mock import patch
import logging
from pandas.util.testing import assert_frame_equal
import pandas as pd
from ab_testing import baselines

logging.disable(logging.CRITICAL)

class TestBaselines(unittest.TestCase):
    srd = baselines.simulate_rate_diff(sample_def = None, success_def = None)
    srd.sample_est = 10
    srd.success_est = 3
    df = pd.DataFrame({'success':[1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0] })
    days = 2
    split = [0.5, 0.5]
    split3 = [1/3, 1/3, 1/3]
    df_splits = [pd.DataFrame({'success':[1,1,1,1,0,0,0,0,0,0] }), pd.DataFrame({'success':[1,1,1,0,0,0,0,0,0,0]}), pd.DataFrame({'success':[1,1,0,0,0,0,0,0,0,0]})]
    
    def test_simulate_data(self):
        actual_df = self.srd.simulate_data(days = self.days)
        expected_df = self.df 
        assert_frame_equal(actual_df, expected_df) 

    def test_divide_data(self):
        dfs = self.srd.divide_data(df = self.df, split = self.split)
        self.assertEqual(dfs[0].shape[0], self.srd.sample_est*self.days*self.split[0])
        self.assertEqual(dfs[1].shape[0], self.srd.sample_est*self.days*self.split[1])
        total_successes = dfs[0].success.sum() +dfs[1].success.sum()
        self.assertEqual(total_successes, self.days*self.srd.success_est)

    def test_get_ratio_diff(self):
        diffs = self.srd.get_ratio_diff(self.df_splits)
        self.assertEqual(diffs[0], .1)
        self.assertEqual(diffs[1], .2)

    def test_simulate_sampling_static(self):
        with patch('ab_testing.baselines.simulate_rate_diff.get_ratio_diff', return_value = [0.1, 0.2]) as mock_ratio_diff:
            max_diff, median_diff = self.srd.simulate_sampling(split = self.split3, df = self.df, iterations = 3)
            self.assertEqual(round(max_diff[0],6), 0.1)
            self.assertEqual(round(median_diff[0], 6), 0.1)
            self.assertEqual(round(max_diff[1], 6), 0.2)
            self.assertEqual(round(median_diff[1], 6), 0.2)

    def test_simulate_sampling_dynamic(self):
        max_diff, median_diff = self.srd.simulate_sampling(split = self.split, df = self.df, iterations = 100)
        self.assertGreaterEqual(max_diff[0], median_diff[0])
        self.assertGreaterEqual(median_diff[0], 0)
        self.assertLessEqual(max_diff[0],1)

