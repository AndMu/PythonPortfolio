import unittest
from datetime import datetime

from PortfolioBasic.Portfolio import PortfolioOrders
from PortfolioBasic.Strategy.BasicStrategies import BollingerBandStrategy, StrategyManager, MACDBollingerBandStrategy
from PortfolioBasic.Strategy.StopLossStrategies import ATRStopLossStrategy
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser


class BollingerBandStrategyTests(unittest.TestCase):

    def setUp(self):
        symbols = ["IBM"]
        self.manager = StrategyManager(symbols, datetime(2007, 12, 31), datetime(2009, 12, 31))
        PortfolioAnalyser.interest_rate = 0
        pass

    def test_construct(self):
        self.manager.process_strategy(BollingerBandStrategy)
        portfolio = PortfolioOrders(self.manager.instruction, 10000)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        self.assertEquals(round(1.00195922396, 5), round(analysis.sharpe_ratio, 5))
        self.assertEquals(round(0.3524, 4), round(analysis.cumulative_return, 4))
        self.assertEquals(round(0.0113472713465, 5), round(analysis.volatility, 5))
        self.assertEquals(13524.0, analysis.portfolio.daily_portfolio_values[-1])
        self.assertEquals(round(0.000716211380412, 5), round(analysis.avg_daily_return, 5))

    def test_construct_two(self):
        symbols = ["IBM", "MSFT"]
        manager = StrategyManager(symbols, datetime(2007, 12, 31), datetime(2009, 12, 31))
        manager.process_strategy(BollingerBandStrategy)
        portfolio = PortfolioOrders(manager.instruction, 10000)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        self.assertEquals(round(0.3685, 4), round(analysis.cumulative_return, 4))
        self.assertEquals(round(1.02532, 5), round(analysis.sharpe_ratio, 5))
        self.assertEquals(round(0.01149, 5), round(analysis.volatility, 5))
        self.assertEquals(13685.0, analysis.portfolio.daily_portfolio_values[-1])
        self.assertEquals(round(0.00074, 5), round(analysis.avg_daily_return, 5))

    def test_MACD_Bollinger(self):
        self.manager.process_strategy(MACDBollingerBandStrategy)
        portfolio = PortfolioOrders(self.manager.instruction, 10000)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)
        self.assertEquals(round(0.362, 4), round(analysis.cumulative_return, 4))
        self.assertEquals(round(0.0099, 5), round(analysis.volatility, 5))
        self.assertEquals(13620.0, analysis.portfolio.daily_portfolio_values[-1])
        self.assertEquals(round(0.000716211380412, 5), round(analysis.avg_daily_return, 5))

    def test_MACD_Bollinger_with_ATRStopLoss(self):

        self.manager.process_strategy(MACDBollingerBandStrategy, ATRStopLossStrategy(0.1, 0.3))
        portfolio = PortfolioOrders(self.manager.instruction, 10000)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        self.assertEquals(round(0.2273, 4), round(analysis.cumulative_return, 4))
        self.assertEquals(round(0.00441, 5), round(analysis.volatility, 5))
        self.assertEquals(12273.0, analysis.portfolio.daily_portfolio_values[-1])
        self.assertEquals(round(0.00045, 5), round(analysis.avg_daily_return, 5))
