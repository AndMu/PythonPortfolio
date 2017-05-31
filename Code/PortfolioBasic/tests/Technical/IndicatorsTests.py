import unittest
from datetime import datetime

from PortfolioBasic.Definitions import HeaderFactory
from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource
from PortfolioBasic.Technical.Analysis import TechnicalPerformance
from PortfolioBasic.Technical.Indicators import MomentumIndicator, BollingerIndicator, RsiIndicator, CombinedIndicator, \
    MACDIndicator


class IndicatorsTest(unittest.TestCase):
    def setUp(self):
        market = LocalMarketDataSource()
        self.symbols = ["IBM"]
        self.prices = market.get_data(self.symbols, datetime(2012, 1, 1), datetime(2012, 12, 1), True)

    def test_momentum(self):
        indicator = MomentumIndicator()
        result = indicator.calculate(self.prices)
        self.assertEquals(6, indicator.required_days())
        self.assertEquals(176, len(result))
        last_row = result.iloc[-1]
        self.assertEquals(0.044760049220672782, last_row[HeaderFactory.MOM])

    def test_Bollinger(self):
        indicator = BollingerIndicator()
        self.assertEquals(20, indicator.required_days())
        result = indicator.calculate(self.prices)
        self.assertEquals(176, len(result))
        last_row = result.iloc[-1]
        self.assertEquals(0.93401469261655201, last_row[HeaderFactory.Bollinger])

    def test_RSI(self):
        indicator = RsiIndicator()
        self.assertEquals(15, indicator.required_days())
        result = indicator.calculate(self.prices)
        self.assertEquals(176, len(result))
        last_row = result.iloc[-1]
        self.assertEquals(0.67590525746192787, last_row[HeaderFactory.RSI])

    def test_Combined(self):
        indicator = CombinedIndicator((RsiIndicator(), BollingerIndicator()))
        self.assertEquals(20, indicator.required_days())
        result = indicator.calculate(self.prices)
        self.assertEquals(176, len(result))

    def test_MACD(self):
        indicator = MACDIndicator()
        self.assertEquals(26, indicator.required_days())
        result = indicator.calculate(self.prices)
        self.assertEquals(176, len(result))
        last_row = result.iloc[-1]
        self.assertEquals(1.4871673578432194, last_row[HeaderFactory.MACD])
        self.assertEquals(0.6848887166431652, last_row[HeaderFactory.MACD_DIFF])
        self.assertEquals(0.80227864120005421, last_row[HeaderFactory.MACD_SIGNAL])

        verification = TechnicalPerformance.compute_macd(self.prices[[HeaderFactory.Price]])
        verification_last_row = result.iloc[-1]
        self.assertEquals(verification_last_row[HeaderFactory.MACD], last_row[HeaderFactory.MACD])
        self.assertEquals(verification_last_row[HeaderFactory.MACD_DIFF], last_row[HeaderFactory.MACD_DIFF])
        self.assertEquals(verification_last_row[HeaderFactory.MACD_SIGNAL], last_row[HeaderFactory.MACD_SIGNAL])

        result = indicator.calculate(self.prices, True)
        last_row = result.iloc[-1]
        self.assertEquals(0.007523893334979043, last_row[HeaderFactory.MACD])
