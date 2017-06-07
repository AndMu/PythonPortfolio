import unittest
from datetime import datetime

import numpy as np

from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource, YahooMarketDataSource
from PortfolioBasic.Portfolio import PortfolioAllocations, Portfolio
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser, TechnicalPerformance, HeaderFactory


class TechnicalPerformanceTest(unittest.TestCase):
    def setUp(self):
        market = LocalMarketDataSource()
        self.symbols = ["IBM", "MSFT"]
        self.prices = market.get_data(self.symbols, datetime(2012, 1, 1), datetime(2012, 12, 1))
        self.prices_single = market.get_data(["IBM"], datetime(2012, 1, 1), datetime(2012, 12, 1), True)

    def test_compute_macd(self):
        macd = TechnicalPerformance.compute_macd(self.prices[self.symbols])
        self.assertEquals(176, len(macd))
        last_row = macd.iloc[-1]
        self.assertEquals(1.4872032677307629, last_row[HeaderFactory.get_name("IBM", HeaderFactory.MACD)])
        self.assertEquals(0.80232900511174032, last_row[HeaderFactory.get_name("IBM", HeaderFactory.MACD_SIGNAL)])
        self.assertEquals(0.68487426261902262, last_row[HeaderFactory.get_name("IBM", HeaderFactory.MACD_HIST)])

    def test_calculate_adr(self):

        adr = TechnicalPerformance.compute_adr(self.prices_single)
        self.assertEquals(176, len(adr))
        last_row = adr.iloc[-1]
        self.assertEquals(2.625714285714285, last_row)


class PortfolioAnalyserTests(unittest.TestCase):
    def setUp(self):
        PortfolioAnalyser.interest_rate = 0
        symbol_list = ['GOOG', 'AAPL', 'GLD', 'XOM']
        allocations = [0.2, 0.3, 0.4, 0.1]
        value = 1000000
        start_date = datetime(2010, 1, 1)
        end_date = datetime(2010, 12, 31)
        self.portfolio1 = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)

        symbol_list = ['AXP', 'HPQ', 'IBM', 'HNZ']
        allocations = np.array([0.0, 0.0, 0.0, 1.0])
        start_date = datetime(2010, 1, 1)
        self.portfolio2 = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)

        symbol_list = ['GOOG', 'AAPL', 'GLD', 'XOM']
        allocations = [0.2, 0.3, 0.4, 0.1]
        start_date = datetime(2010, 6, 1)
        end_date = datetime(2010, 12, 31)
        self.portfolio3 = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)

        symbol_list = ['YHOO', 'HPQ', 'GLD', 'HNZ']
        allocations = [0.2, 0.3, 0.4, 0.1]
        self.portfolio4 = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)

    def tearDown(self):
        PortfolioAnalyser.interest_rate = 0
        Portfolio.resources = LocalMarketDataSource()

    def test_assess_portfolio_case_1(self):
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio1)
        self.assertEquals(0.25564678453350465, analysis.cumulative_return)
        self.assertEquals(0.010010402800015371, analysis.volatility)
        self.assertEquals(0.00095736623423814133, analysis.avg_daily_return)
        self.assertEquals(1.5181924364126345, analysis.sharpe_ratio)

        PortfolioAnalyser.interest_rate = 0.01
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio1)
        self.assertEquals(1.4555751457946318, analysis.sharpe_ratio)

    def test_assess_portfolio_case_2(self):
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio2)
        self.assertEquals(0.19810596365497823, analysis.cumulative_return)
        self.assertEquals(0.0092615312876845723, analysis.volatility)
        self.assertEquals(0.00076310615267202893, analysis.avg_daily_return)
        self.assertEquals(1.3079839874416059, analysis.sharpe_ratio)

        PortfolioAnalyser.interest_rate = 0.01
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio2)
        self.assertEquals(1.24030357025559, analysis.sharpe_ratio)

    def test_assess_portfolio_case_3(self):
        Portfolio.resources = YahooMarketDataSource()
        self.portfolio3.fill_data()
        PortfolioAnalyser.interest_rate = 0
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio3)
        self.assertEquals(round(0.20511393879215278, 2), round(analysis.cumulative_return, 2))
        self.assertEquals(round(0.0092973461970739923, 4), round(analysis.volatility, 4))
        self.assertEquals(round(0.0012958692436644658, 4), round(analysis.avg_daily_return, 4))
        self.assertEquals(round(2.2125976667229321, 2), round(analysis.sharpe_ratio, 2))

        PortfolioAnalyser.interest_rate = 0.01
        analysis = PortfolioAnalyser.assess_portfolio(self.portfolio3)
        self.assertEquals(round(2.1451779656549967, 2), round(analysis.sharpe_ratio, 2))

    def test_optimize_portfolio1(self):
        PortfolioAnalyser.optimize_portfolio(self.portfolio1)
        performance = PortfolioAnalyser.assess_portfolio(self.portfolio1)
        """Optimal allocations: [  5.38105153e-16   3.96661695e-01   6.03338305e-01  -5.42000166e-17]
        Sharpe Ratio: 2.00401501102
        Volatility (stdev of daily returns): 0.0101163831312
        Average Daily Return: 0.00127710312803
        Cumulative Return: 0.360090826885"""
        self.assertEquals(round(0.360090826885, 2), round(performance.cumulative_return, 2))
        self.assertEquals(round(0.0101163831312, 4), round(performance.volatility, 4))
        self.assertEquals(round(0.00127710312803, 4), round(performance.avg_daily_return, 4))
        self.assertEquals(round(2.00401501102, 2), round(performance.sharpe_ratio, 2))

    def test_optimize_portfolio2(self):
        self.portfolio2.start_date = datetime(2004, 1, 1)
        self.portfolio2.end_date = datetime(2006, 1, 1)
        self.portfolio2.fill_data()
        PortfolioAnalyser.optimize_portfolio(self.portfolio2)
        performance = PortfolioAnalyser.assess_portfolio(self.portfolio2)
        """Start Date: 2004-01-01
            End Date: 2006-01-01
            Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
            Optimal allocations: [  7.75113042e-01   2.24886958e-01  -1.18394877e-16  -7.75204553e-17]
            Sharpe Ratio: 0.842697383626
            Volatility (stdev of daily returns): 0.0093236393828
            Average Daily Return: 0.000494944887734
            Cumulative Return: 0.255021425162"""
        self.assertEquals(round(0.255021425162, 2), round(performance.cumulative_return, 2))
        self.assertEquals(round(0.0093236393828, 4), round(performance.volatility, 4))
        self.assertEquals(round(0.000494944887734, 4), round(performance.avg_daily_return, 4))
        self.assertEquals(round(0.842697383626, 2), round(performance.sharpe_ratio, 2))


if __name__ == '__main__':
    unittest.main()
