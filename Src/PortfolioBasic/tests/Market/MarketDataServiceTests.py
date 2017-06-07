import unittest
from datetime import datetime

from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource, YahooMarketDataSource


class LocalMarketDataSourceTests(unittest.TestCase):

    def test_construct(self):
        resources = LocalMarketDataSource()
        self.assertEquals(1005, len(resources.indexes))
        self.assertTrue("AAPL" in resources.indexes)
        self.assertTrue("Test" not in resources.indexes)

    def test_get_data(self):
        resources = LocalMarketDataSource()
        result = resources.get_data(['GOOG'], start_date=datetime(2005, 1, 1), end_date=datetime(2005, 2, 1))
        self.assertEquals(21, len(result))


class YahooMarketDataSourceTests(unittest.TestCase):

    def test_get_data(self):
        resources = YahooMarketDataSource()
        result = resources.get_data(['GOOG'], start_date=datetime(2005, 1, 1), end_date=datetime(2005, 2, 1))
        self.assertEquals(21, len(result['GOOG']))


