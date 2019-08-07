from ab_testing import baselines
from ab_testing.queries import queries_dict
from ab_testing.stats import non_inferiority, superiority
from ab_testing import utils

#logging
logger = utils.setup_logger(__name__)
logger.info('\n\n')
logger.info('Running Power Analysis\n\n')

#setup
needs = queries_dict['needs']
bookings = queries_dict['bookings'].format(lag = 14)
days = 60
logger.info('Simulating {} days worth of data'.format(days))
split = 0.5
logger.info('Test split: Control {0}%, Variation {1}%'.format(int(split*100), int((1-split)*100)) )

#simulate
ss = baselines.simulate_rate_diff(sample_def = needs, success_def = bookings)
ss.estimate_samples()
ss.estimate_successes()
df = ss.simulate_data(days = days)
max_diff, mean_diff = ss.simulate_sampling(df = df, split = split, iterations = 1000)

#power analysis
delta = -max_diff
pA = (ss.success_est/ss.sample_est)-mean_diff/2
pB = (ss.success_est/ss.sample_est)+mean_diff/2
kappa = (1-split)/split
nB = ss.sample_est*60/2
power = 0.9

ni = non_inferiority(delta = delta, pA = pA, pB = pB, kappa = kappa, nB = nB, power = power, samples_per_day = ss.sample_est)
ni.calc_power()
ni.calc_samples()

delta = max_diff
s = superiority(delta = delta, pA = pA, pB = pB, kappa = kappa, nB = nB, power = power, samples_per_day = ss.sample_est)
s.calc_power()
s.calc_samples()

