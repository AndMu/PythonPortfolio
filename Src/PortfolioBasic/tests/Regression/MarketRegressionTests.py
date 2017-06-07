import logging
import os.path
import unittest

from ddt import ddt, data

from PortfolioBasic.Portfolio import PortfolioOrdersFactory, PortfolioOrdersLeverageManager
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser
from PortfolioBasic.tests.Data.MarketsimTestCase import MarketsimTestCaseData, MarketsimTestCase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@ddt
class MarketRegressionTests(unittest.TestCase):
    @data(*MarketsimTestCaseData.marketsim_test_cases)
    def test_construct_case(self, value: MarketsimTestCase):

        logging.info("Running: <%s> %s", value.group, value.description)
        PortfolioAnalyser.interest_rate = 0
        file = os.path.join('../ml4t/mc2p1', value.inputs["orders_file"])
        start_value = value.inputs["start_val"]
        portfolio = PortfolioOrdersFactory.load(file, start_value)
        if portfolio.is_over_leveraged():
            portfolio = PortfolioOrdersLeverageManager.deleverage(portfolio)

        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        if 'num_days' in value.outputs:
            self.assertEquals(value.outputs['num_days'], len(portfolio.daily_portfolio_values))

        if 'last_day_portval' in value.outputs:
            self.assertEquals(round(value.outputs['last_day_portval'], 1), round(portfolio.daily_portfolio_values[-1],
                                                                                 1))

        if 'sharpe_ratio' in value.outputs:
            self.assertEquals(round(value.outputs["sharpe_ratio"], 10), round(analysis.sharpe_ratio, 10))

        if 'avg_daily_ret' in value.outputs:
            self.assertEquals(round(value.outputs["avg_daily_ret"], 10), round(analysis.avg_daily_return, 10))
