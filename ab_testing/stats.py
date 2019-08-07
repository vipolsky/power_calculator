from math import ceil
from scipy.stats import norm
from ab_testing import utils


logger = utils.setup_logger(__name__)

class base:
    def __init__(self, delta, pA, pB, kappa, nB, alpha, power, samples_per_day):
        self.delta = delta                      #non-inferiority margin
        self.pA = pA                            #variant success proportion
        self.pB = pB                            #control success proportion
        self.kappa = kappa                      #sampling ratio, nA/nB
        self.nB = nB                            #control sample size
        self.alpha = alpha                      #type I error rate
        self.power = power                      #power, 1-type II error 
        self.samples_per_day = samples_per_day  #samples per day

    def calc_power(self):
        logger.info('Calculating power...')
        try: 
            nA = self.kappa*self.nB    
            z = (self.pA-self.pB-self.delta)/ (self.pA*(1-self.pA)/nA + self.pB*(1-self.pB)/self.nB)**(.5)
            power = norm.cdf(z-norm.ppf(1-self.alpha))+norm.cdf(-z-norm.ppf(1-self.alpha))
            power = round(power, 6)
            logger.info('''\n
                    {0} days worth of samples =\t{1}
                    Absolute delta =\t\t{2}
                    Significance =\t\t{3}%\n
                    {4}% power\n'''.format(
                        int((nA+self.nB)/self.samples_per_day),
                        int(nA+self.nB), 
                        self.delta, 
                        int((1-self.alpha)*100), 
                        round(power*100, 1)
                        )
                    )
            return power
        except:
            logger.debug('Make sure delta, pA, pB, kappa, nB, and alpha are not None')

    def calc_samples(self):
        logger.info('Calculating samples needed...')
        try:
            samples = (self.pA*(1-self.pA)/self.kappa + self.pB*(1-self.pB))*((norm.ppf(1-self.alpha)+norm.ppf(self.power))/(self.pA-self.pB-self.delta))**(2)
            samples = ceil(samples)
            logger.info('''\n
                    Significance =\t{0}%
                    Absolute delta =\t{1}
                    Power =\t{2}%\n
                    {3} samples total, {4} days\n'''.format(
                        int((1-self.alpha)*100), 
                        self.delta, 
                        round(self.power*100, 1), 
                        int(samples+self.kappa*samples),
                        int((samples+self.kappa*samples)/self.samples_per_day)
                        )
                    )
            return samples
        except:
            logger.debug('Make sure delta, pA, pB, kappa, alpha, and power are not None')
       
class non_inferiority(base):
    def __init__(self, delta, pA, pB, kappa, nB = None, alpha = .05, power = None, samples_per_day = None):
        if delta > 0:
            logger.debug('delta value must be negative for a non-inferiority test')
            raise ValueError
        else:
            logger.info('\nRunning non-inferiority power calculation\n')
            base.__init__(self, delta, pA, pB, kappa, nB, alpha, power, samples_per_day)

class superiority(base):
    def __init__(self, delta, pA, pB, kappa, nB = None, alpha = .05, power = None, samples_per_day = None):
        if delta < 0:
            logger.debug('delta value must be positive for a non-inferiority test')
            raise ValueError
        else:
            logger.info('\nRunning superiority power calculation\n')
            base.__init__(self, delta, pA, pB, kappa, nB, alpha, power, samples_per_day)

