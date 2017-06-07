import datetime
import logging

import pandas as pd

from PortfolioBasic.Definitions import HeaderFactory, Utilities
from PortfolioBasic.MachineLearning.SimpleAlgoTrader import BaseAlgoTrader
from PortfolioBasic.Portfolio import PortfolioOrders
from PortfolioBasic.Strategy.BasicStrategies import BaseStrategy
from PortfolioBasic.Strategy.ExitStrategies import ExitStrategy, DayExitStrategy
from PortfolioBasic.Strategy.StopLossStrategies import StopLossStrategy, ATRStopLossStrategy

logger = logging.getLogger(__name__)


class MachineStrategyManager(object):

    def __init__(self, symbol: str, algo: BaseAlgoTrader):
        self.symbols = [symbol]
        self.algo = algo

    def train_strategy(self, start_date: datetime, end_date: datetime):
        logger.info("Training %s %s - %s", self.symbols[0], start_date.isoformat(), end_date.isoformat())
        df_prices = PortfolioOrders.resources.get_data(self.symbols, start_date, end_date, True)
        Utilities.fill_missing_values(df_prices)
        self.algo.train(df_prices)

    def process_strategy(self, start_date: datetime, end_date: datetime, threshold=0.005):
        logger.info("Processing %s %s - %s", self.symbols[0], start_date.isoformat(), end_date.isoformat())
        original_date = start_date
        start_date = start_date - datetime.timedelta(days=self.algo.indicators.required_days() * 2)
        df_prices = PortfolioOrders.resources.get_data(self.symbols, start_date, end_date, True)
        Utilities.fill_missing_values(df_prices)
        stop_loss = ATRStopLossStrategy()
        stop_loss.pre_process(df_prices)
        created = MachineStrategy(self.symbols,
                                  self.algo,
                                  df_prices,
                                  DayExitStrategy(self.algo.prediction_days, stop_loss),
                                  original_date,
                                  end_date,
                                  threshold=threshold,
                                  dump=self.algo.dump)
        if len(created.instructions) != 1:
            raise ValueError("Invalid amount of instructions")
        instruction = created.instructions[0]
        instruction.index.name = "Date"
        return instruction.ix[original_date.isoformat():end_date.isoformat()]


class MachineStrategy(BaseStrategy):
    def __init__(self, symbols: list, algo: BaseAlgoTrader, df_prices: pd.DataFrame, exit: ExitStrategy,
                 from_date: datetime, end_date: datetime, threshold=0.01, dump=False):
        if len(symbols) != 1:
            raise ValueError('Only 1 symbol can be used')
        self.exit = exit
        self.threshold = threshold
        self.algo = algo
        self.result, self.rmse, self.c = self.algo.predict(df_prices)
        self.result = self.result.ix[from_date.isoformat():end_date.isoformat()]
        df_prices = df_prices.ix[from_date.isoformat():end_date.isoformat()]
        logger.info("Training result [%s] RMSE:%f Correliation:%f", symbols[0], self.rmse, self.c)
        super(MachineStrategy, self).__init__(symbols, df_prices, None, dump)

    def full_exit(self, data: pd.DataFrame, instruction: pd.DataFrame) -> pd.DataFrame:
        return self.exit.process_exit(instruction)

    def process_exit(self, data: pd.DataFrame, instructions: pd.DataFrame):
        return None

    def process_buy(self, data: pd.DataFrame):
        mask = data.loc[(data[HeaderFactory.MACHINE] >= self.threshold)]
        return mask

    def process_sell(self, data: pd.DataFrame):
        mask = data.loc[(data[HeaderFactory.MACHINE] <= -self.threshold)]
        return mask

    def setup_data(self, symbol: str) -> pd.DataFrame:
        instruction = super(MachineStrategy, self).setup_data(symbol)
        instruction = instruction.join(self.result)
        return instruction
