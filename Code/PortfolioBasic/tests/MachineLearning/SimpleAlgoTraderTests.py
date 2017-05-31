import unittest
from datetime import datetime

from PortfolioBasic.MachineLearning.SimpleAlgoTrader import LinearAlgoTrader
from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource
from PortfolioBasic.Technical.Indicators import MomentumIndicator, BollingerIndicator, RsiIndicator, CombinedIndicator


class SimpleAlgoTraderTests(unittest.TestCase):

    def setUp(self):
        market = LocalMarketDataSource()
        self.symbols = ["IBM"]
        self.train_prices = market.get_data(self.symbols, datetime(2008, 1, 1), datetime(2010, 12, 1), True)
        self.test_prices = market.get_data(self.symbols, datetime(2011, 1, 1), datetime(2012, 12, 1), True)

    def test_train(self):
        indicators = CombinedIndicator((MomentumIndicator(), BollingerIndicator(), RsiIndicator()))
        algo = LinearAlgoTrader(indicators)
        algo.train(self.train_prices)
        data, rmse, c = algo.predict(self.test_prices)
        self.assertEquals(0.027115168423577626, rmse)
        self.assertEquals(0.25628745701762157, c)
