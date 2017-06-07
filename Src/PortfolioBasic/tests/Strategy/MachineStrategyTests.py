import unittest
from datetime import datetime
from PortfolioBasic.MachineLearning.SimpleAlgoTrader import LinearAlgoTrader
from PortfolioBasic.Portfolio import PortfolioOrders
from PortfolioBasic.Strategy.MachineStrategy import MachineStrategyManager
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser
from PortfolioBasic.Technical.Indicators import CombinedIndicator, MomentumIndicator, BollingerIndicator, RsiIndicator, \
    MACDIndicator


class MachineStrategyTests(unittest.TestCase):

    def setUp(self):
        PortfolioAnalyser.interest_rate = 0
        pass

    def test_construct(self):
        indicators = CombinedIndicator((MomentumIndicator(), BollingerIndicator(), RsiIndicator(), MACDIndicator()))
        algo = LinearAlgoTrader(indicators)
        manager = MachineStrategyManager('IBM', algo)
        from_date = datetime(2007, 12, 31)
        to_date = datetime(2009, 12, 31)
        manager.train_strategy(from_date, to_date)

        from_date = datetime(2009, 12, 31)
        to_date = datetime(2010, 12, 31)
        # from_date = datetime(2007, 12, 31)
        # to_date = datetime(2009, 12, 31)
        instructions = manager.process_strategy(from_date, to_date, threshold=0.01)

        portfolio = PortfolioOrders(instructions, 10000, to_date)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        self.assertEquals(round(0.3524, 4), round(analysis.cumulative_return, 4))
        # self.assertEquals(round(1.00195922396, 5), round(analysis.sharpe_ratio, 5))
        # self.assertEquals(round(0.0113472713465, 5), round(analysis.volatility, 5))
        # self.assertEquals(13524.0, analysis.portfolio.daily_portfolio_values[-1])
        # self.assertEquals(round(0.000716211380412, 5), round(analysis.avg_daily_return, 5))

    def test_MC3_2(self):
        indicators = CombinedIndicator((MomentumIndicator(), BollingerIndicator(), RsiIndicator()))
        algo = LinearAlgoTrader(indicators)
        manager = MachineStrategyManager('IBM', algo)
        manager.train_strategy(datetime(2007, 12, 31), datetime(2009, 12, 31))