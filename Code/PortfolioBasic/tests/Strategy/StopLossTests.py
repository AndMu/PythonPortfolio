import unittest
from datetime import datetime

from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource
from PortfolioBasic.Strategy.StopLossStrategies import ATRStopLossStrategy


class ATRStopLossStrategyTests(unittest.TestCase):

    def setUp(self):
        symbols = ["IBM"]
        market = LocalMarketDataSource()
        self.prices_single = market.get_data(["IBM"], datetime(2012, 1, 1), datetime(2012, 12, 1), True)
        pass

    def test_single_exit(self):
        strategy = ATRStopLossStrategy()
        strategy.pre_process(self.prices_single)
        low, high = strategy.get_exit( datetime(2012, 6, 6))
        self.assertEqual(184.51714285714286, low)
        self.assertEqual(202.25428571428571, high)
        low, high = strategy.get_exit(datetime(2012, 6, 6), True)
        self.assertEqual(181.7657142857143, low)
        self.assertEqual(199.50285714285715, high)

