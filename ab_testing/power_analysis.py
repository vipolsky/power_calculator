import numpy as np
import pandas as pd
from scipy.stats import norm
from roverdata.db import DataWarehouse
from ab_testing import utils
from ab_testing.queries import queries_dict


logger = utils.setup_logger(__name__)

class power_analysis:
    def __init__(self, split, metric, days, delta, lag, alpha):
        """
        Args:
            split (list): list of floats,
                where first float represents the proportion of data
                that will go to the control and the following floats
                represent the variations
                if len(split) > 2, power calculation will run for the
                smaller of the two variation proportions
            metric (string): success metric to be used (pick from items in ab_testing.queries.queries_dict)
            days (int): will be used to estimate a conservative
                delta if none is provided
            delta (float): optional, difference in proportions we would like to detect
            lag (int): optional, if using a "_lagged" metric, specify the lag to be used
            alpha (float): optional, significance level
        """
        self.metric = metric
        self.lag = lag
        self.control_prop = split.pop(0)
        self.variation_prop = min(split)
        self.days = days
        self.alpha = alpha
        self.samples_per_day, self.successes_per_day = self.fetch_successes_and_samples()
        self.n_control = self.samples_per_day * self.days * self.control_prop
        self.n_variation = self.samples_per_day * self.days * self.variation_prop
        self.p = self.successes_per_day / self.samples_per_day

    def fetch_successes_and_samples(self):
        """Get the expected number of successes and samples per day
        for the inputted success metric and optional lag"""
        logger.debug('Connecting to datawarehouse')
        db = DataWarehouse()
        if self.lag is not None:
            query = queries_dict[self.metric].format(lag = self.lag)
            logger.debug('Lag set to {}'.format(self.lag))
        else:
            query = queries_dict[self.metric]
        logger.debug('Fetching number of samples and success expected per day')
        df = db.query(query)
        df.rename(columns = {df.columns[0]:'samples_per_day', df.columns[1]:'successes_per_day'}, inplace = True)
        samples = df.samples_per_day.values[0]
        successes = df.successes_per_day.values[0]
        return samples, successes

    def calculate_expected_delta(self):
        """
        Get the "max" expected delta in proportions
        given an inputted number of days to simulate
        Observed delta should be smaller than "max" delta 99.93% of the time
        assuming there is actually no difference in proportions
            (a.k.a the difficult to detect case)

        Returns:
            float: expected "max" delta
        """
        std_dev_control = (self.n_control*self.p*(1-self.p))**(.5)
        std_dev_variation = (self.n_variation*self.p*(1-self.p))**(.5)
        plus_std_dev_control = ((self.n_control*self.p)+(2*std_dev_control))/self.n_control
        minus_std_dev_variation = ((self.n_variation*self.p)-(2*std_dev_variation))/self.n_variation
        return plus_std_dev_control-minus_std_dev_variation


    def calculate_power(self):
        """
        Returns:
            float: power
        """
        z = -self.delta/(self.p*(1-self.p)/self.n_variation + self.p*(1-self.p)/self.n_control)**(.5)
        power = norm.cdf(z-norm.ppf(1-self.alpha))+norm.cdf(-z-norm.ppf(1-self.alpha))
        logger.info('''\n
                days =\t\t\t{0}
                samples =\t\t{1}
                delta =\t\t\t{2}
                significance =\t\t{3}%
                variant proportion =\t{4}
                control proportion =\t{5}\n
                power = \t\t{6}%\n'''.format(
            self.days,
            self.days*self.samples_per_day,
            round(self.delta, 6),
            int((1 - self.alpha) * 100),
            round(self.p, 4),
            round(self.p, 4),
            round(power * 100, 1)
            )
        )
        return round(power, 6)

class non_inferiority_power_analysis(power_analysis):
   def __init__(self, split, metric, days=30, delta=None, lag=None, alpha=.05):
        power_analysis.__init__(self, split, metric, days, delta, lag, alpha)
        if delta is None:
            self.delta = self.calculate_expected_delta()*(-1)
        elif delta > 0:
            self.delta = delta*(-1)
        else:
            self.delta = delta

class superiority_power_analysis(power_analysis):
   def __init__(self, split, metric, days=30, delta=None, lag=None, alpha=.05):
        power_analysis.__init__(self, split, metric, days, delta, lag, alpha)
        if delta is None:
            self.delta = self.calculate_expected_delta()
        elif delta < 0:
            self.delta = delta*(-1)
        else:
            self.delta = delta
