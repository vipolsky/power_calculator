from ab_testing.power_analysis import non_inferiority_power_analysis, superiority_power_analysis
from ab_testing import utils

#logging
logger = utils.setup_logger(__name__)
logger.info('\n\n')
logger.info('Running Power Analysis\n\n')

power = non_inferiority_power_analysis(split = [.5, .5], metric='need_to_book_lagged', lag = 7, days = 30, delta = .003).calculate_power()
power = superiority_power_analysis(split = [.5, .5], metric='need_to_book_lagged', lag = 7, days = 30, delta = .003).calculate_power()
