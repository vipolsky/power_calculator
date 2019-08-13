import numpy as np
import pandas as pd 
from sklearn.model_selection import train_test_split
from roverdata.db import DataWarehouse
from ab_testing import utils

logger = utils.setup_logger(__name__)

class simulate_rate_diff:
    def __init__(self, metric):
        self.db = DataWarehouse()
        self.metric = metric

    def fetch_successes_and_samples(self):
        '''Get the expected number of successes and samples per day'''
        logger.debug('Gathering expected successes and samples per day\n\n{}\n\n'.format(self.metric))
        df = self.db.query(self.metric)
        df.rename(columns = {df.columns[0]:'samples_per_day', df.columns[1]:'successes_per_day'}, inplace = True)
        self.sample_est = df.samples_per_day.values[0]
        self.success_est = df.successes_per_day.values[0]

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

    def divide_data(self, df, split, **kwargs):
        '''Given a dataframe of samples and their successes, 
        split it according to split parameter
        
        Args:
            df (pandas.DataFrame): dataframe containing samples and their successes
            split (list of floats): list of floats representing the proportion of data for the control first then all the variations, must sum to one

        Returns:
            list: splits of `df`, of length `splits`
        '''
        if 'seed' in kwargs:
            np.random.seed(kwargs['seed'])
        if sum(split) != 1 or not isinstance(split, list):
            logger.debug('split must be a list of floats summing to one, control is at index 0')
            raise ValueError
        df_lens = [int(x*len(df)) for x in split]
        del df_lens[-1]
        df_indexes = np.cumsum(df_lens)
        df_indexs = [x+1 if ind > 0 else x for ind, x in enumerate(df_indexes)]
        df_splits = np.split(df.sample(frac=1), df_indexes)
        return df_splits 

    def get_ratio_diff(self, df_splits):
        '''Give a list of dataframes containing samples and their successes, 
        compute the absolute value of the difference between the control success ratio and each variant

        Args:
            df_splits (list): list of pandas.DataFrame's, dataframe at index 0 represents the control, all subsequest dataframes are variants

        Returns:
            list: list of floats representing the absolute value of the success ratios of the control vs each variant. Of length splits-1
        '''
        diffs = []
        control = df_splits.pop(0)
        for i in range(len(df_splits)):
            variation = df_splits.pop(0)
            control_rate = control.success.sum()/control.shape[0]
            variation_rate = variation.success.sum()/variation.shape[0]
            diffs.append(abs(round(control_rate-variation_rate, 6)))
        return diffs

    def simulate_sampling(self, df, split, iterations):
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
        max_diff = [0.0]*(len(split)-1)
        total_diff = [0.0]*(len(split)-1)
        for i in range(iterations):
            diffs = self.get_ratio_diff(self.divide_data(df = df, split = split, seed = i))
            total_diff = [x + y for x, y in zip(total_diff, diffs)]
            max_diff = [y if y > x else x for x, y in zip(max_diff, diffs)]

        median_diff = [x/iterations for x in total_diff]
        median_diff = [round(x, 6) for x in median_diff]
        max_diff = [round(x, 6) for x in max_diff]

        variation = 1
        for diff in zip(max_diff, median_diff):
            logger.info('''\tFor Variation {var}:\n 
            Maximum difference observed = {max_diff}
            Median difference observed = {med_diff}\n'''.format(
                var = variation, max_diff = diff[0], med_diff = diff[1]
                )
            )
            variation += 1
        return max_diff, median_diff


