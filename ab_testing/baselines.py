import numpy as np
import pandas as pd 
from sklearn.model_selection import train_test_split
from roverdata.db import DataWarehouse
from ab_testing import utils

logger = utils.setup_logger(__name__)

class simulate_rate_diff:
    def __init__(self, sample_def, success_def):
        self.db = DataWarehouse()
        self.sample_def = sample_def
        self.success_def = success_def

    def estimate_samples(self):
        '''Get the expected number of samples per day'''
        logger.debug('Gathering expected samples per day\n\n{}\n\n'.format(self.sample_def))
        samples_per_day_df = self.db.query(self.sample_def)
        samples_per_day_df.rename(columns = {samples_per_day_df.columns[0]:'samples_per_day'}, inplace = True)
        self.sample_est = samples_per_day_df.samples_per_day.values[0]

    def estimate_successes(self):
        '''Get the expected number of successes per day'''
        logger.debug('Gathering expected successes per day\n\n{}\n\n'.format(self.success_def))
        successes_per_day_df = self.db.query(self.success_def)
        successes_per_day_df.rename(columns = {successes_per_day_df.columns[0]:'successes_per_day'}, inplace = True)
        self.success_est = successes_per_day_df.successes_per_day.values[0]

    def simulate_data(self, days):
        '''Create a dataset with the expected number of 
        samples and their successes for an inputted number of days

        Args:
            days (int): number of days to simulate data for

        Returns:
            pandas.DataFrame: simulated dataset for a time period of `days`
        '''
        logger.debug('Simulating data... \n')
        df = pd.DataFrame(np.zeros(self.sample_est*days).astype(int) , columns = ['success'])
        df.loc[:(self.success_est*days)-1,'success'] = 1
        return df

    def get_rate_diff(self, df, split, **kwargs):
        '''Given a dataframe of samples and their successes, 
        split it and compute the difference in success ratio
        
        Args:
            df (pandas.DataFrame): dataframe containing samples and their successes
            split (float): ratio for A/B test, a split of 0.6 means that the simulated control 
            would get 60% of the data

        Returns:
            flaot: absolute value of the difference in success rates
        '''
        control, variation = train_test_split(df, test_size=split, **kwargs)
        control_rate = control.success.sum()/control.shape[0]
        variation_rate = variation.success.sum()/variation.shape[0]
        return abs(control_rate-variation_rate)

    def simulate_sampling(self, df, split, iterations = 1000):
        '''Sample from the simulated data

        Args:
            df (pandas.DataFrame): dataframe containing samples and their successes
            split (float): ratio for A/B test
            iterations (int): number of simulations 

        Returns:
            max_diff (float): maximum success ratio difference observed 
            median_diff (float): median success ratio difference observed
        '''
        logger.debug('Sampling data ... \n')
        max_diff = 0.0
        total_diff = 0.0
        for i in range(iterations):
            diff = self.get_rate_diff(df, split)
            total_diff += diff
            if diff > max_diff:
                max_diff = diff

        median_diff = round(total_diff/iterations, 6)
        max_diff = round(max_diff, 6)
        logger.info('Maximum difference observed = {}'.format(max_diff))
        logger.info('Medium difference observed = {}'.format(median_diff))
        return max_diff, median_diff


