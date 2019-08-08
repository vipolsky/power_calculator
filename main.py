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
split = [1/3, 1/3, 1/3]

#simulate and sample
ss = baselines.simulate_rate_diff(sample_def = needs, success_def = bookings)
ss.estimate_samples()
ss.estimate_successes()
df = ss.simulate_data(days = days)
logger.info('\tControl Baseline:\t\t\t{}'.format(ss.success_est/ss.sample_est))
logger.info('\tTotal Expected Samples Per Day: \t{}'.format(ss.sample_est))
max_diff, mean_diff = ss.simulate_sampling(df = df, split = split, iterations = 1000)

for i in range(len(max_diff)):
    logger.info('\t\tAnalyzing Variation {}'.format(i+1))
    max_diff_var = max_diff[i]
    mean_diff_var = mean_diff[i]

    #power analysis
    delta = max_diff_var
    pA = (ss.success_est/ss.sample_est)-mean_diff_var/2
    pB = (ss.success_est/ss.sample_est)+mean_diff_var/2
    kappa = split[i+1]/split[0]
    nB = ss.sample_est*days*split[0]
    power = 0.9
    samples_per_day = ss.sample_est*split[0]+ss.sample_est*split[i+1]


    s = superiority(delta = delta, pA = pA, pB = pB, kappa = kappa, nB = nB, power = power, samples_per_day = samples_per_day)
    s.calc_power()
    s.calc_samples()

    s = superiority(delta = delta, pA = pA-0.01, pB = pB, kappa = kappa, nB = nB, power = .95, samples_per_day = samples_per_day)
    s.calc_samples()

