import unittest
from datetime import datetime

from ddt import ddt, data

from PortfolioBasic.Portfolio import PortfolioAllocations
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser
from PortfolioBasic.tests.Data.PortfolioTestCase import PortfolioTestCaseData, PortfolioTestCase


@ddt
class PortfolioRegressionTests(unittest.TestCase):

    @data(*PortfolioTestCaseData.portfolio_test_cases)
    def test_construct_case(self, value: PortfolioTestCase):

        allocations_table = value.inputs["symbol_allocs"]
        allocations = []
        symbol_list = []
        for item in allocations_table:
            symbol_list.append(item)
            allocations.append(allocations_table[item])
        start_date = datetime.strptime(value.inputs["start_date"], '%Y-%m-%d')
        end_date = datetime.strptime(value.inputs["end_date"], '%Y-%m-%d')
        portfolio_value = value.inputs["start_val"]
        portfolio = PortfolioAllocations(symbol_list, allocations, start_date, end_date, portfolio_value)

        PortfolioAnalyser.interest_rate = 0
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        self.assertEquals(round(value.outputs["cum_ret"], 10), round(analysis.cumulative_return, 10))
        self.assertEquals(round(value.outputs["avg_daily_ret"], 10), round(analysis.avg_daily_return, 10))
        self.assertEquals(round(value.outputs["sharpe_ratio"], 10), round(analysis.sharpe_ratio, 10))


