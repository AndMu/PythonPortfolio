import abc
import datetime

import pandas as pd

from PortfolioBasic.Portfolio import PortfolioOrders
from PortfolioBasic.Strategy.StopLossStrategies import StopLossStrategy
from PortfolioBasic.Technical.Analysis import TechnicalPerformance, HeaderFactory


class StrategyManager(object):
    def __init__(self, symbols: list, start_date: datetime, end_date: datetime):
        self.symbols = symbols
        self.df_prices = PortfolioOrders.resources.get_data(symbols, start_date, end_date)
        self.instruction = pd.DataFrame(index=["Date"], columns=["Symbol", HeaderFactory.Order, "Shares"])

    def process_strategy(self, strategy, stop_loss=None):
        created = strategy(self.symbols, self.df_prices, stop_loss)
        strategy_instructions = created.instructions
        for instruction in strategy_instructions:
            self.instruction = self.instruction.append(instruction[self.instruction.columns])
            self.instruction = self.instruction.dropna()
            self.instruction.index.name = "Date"


class StrategyDataFactory(object):
    @staticmethod
    def construct_instructions(symbol, df_prices: pd.DataFrame):
        instruction = df_prices
        instruction["Symbol"] = symbol
        instruction[HeaderFactory.Order] = None
        instruction["Shares"] = 100
        return instruction


class BaseStrategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, symbols: list, df_prices: pd.DataFrame, stop_loss: StopLossStrategy = None, dump=False):
        self.instructions = []
        self.stop_loss = stop_loss
        self.df_prices = df_prices
        self.dump = dump
        for symbol in symbols:
            data = self.setup_data(symbol)
            symbol_instructions = self.process_symbol(data)
            self.instructions.append(symbol_instructions)
            symbol_instructions.to_csv("{}_instructions.csv".format(symbol))

    def process_symbol(self, data: pd.DataFrame):
        instruction = data.copy()
        buy_instructions = self.process_buy(data)
        instruction.loc[buy_instructions.index, HeaderFactory.Order] = HeaderFactory.BUY

        sell_instructions = self.process_sell(data)
        instruction.loc[sell_instructions.index, HeaderFactory.Order] = HeaderFactory.SELL

        if self.dump:
            instruction.to_csv("ins_buy_sell.csv")

        instruction = self.full_exit(data, instruction)

        if self.dump:
            instruction.to_csv("ins_after_stop.csv")

        previous_instruction = instruction.shift(1)
        instruction.loc[(instruction[HeaderFactory.Order] == HeaderFactory.EXIT) & 
                        (previous_instruction[HeaderFactory.Order] == HeaderFactory.BUY), HeaderFactory.Order] = \
            HeaderFactory.SELL
        instruction.loc[(instruction[HeaderFactory.Order] == HeaderFactory.EXIT) & 
                        (previous_instruction[HeaderFactory.Order] == HeaderFactory.SELL), HeaderFactory.Order] = \
            HeaderFactory.BUY

        return instruction[instruction[HeaderFactory.Order] != HeaderFactory.EXIT]

    def full_exit(self, data: pd.DataFrame, instruction: pd.DataFrame) -> pd.DataFrame:
        exit_instructions = self.process_exit(data, instruction)
        instruction.loc[exit_instructions.index, HeaderFactory.Order] = HeaderFactory.EXIT
        if self.dump:
            instruction.to_csv("ins_before_stop_dup.csv")
        instruction = self.remove_dublicates(instruction)

        if self.dump:
            instruction.to_csv("ins_before_stop.csv")

        if self.stop_loss is not None:
            instruction = self.stop_loss.process(data, instruction)
            instruction = self.remove_dublicates(instruction)

        return instruction

    def remove_dublicates(self, instruction: pd.DataFrame):
        unique = instruction.dropna()
        previous_instruction = unique.shift(1)
        mask = unique.loc[unique[HeaderFactory.Order] != previous_instruction[HeaderFactory.Order], :]
        return instruction.loc[mask.index, :].copy()

    def setup_data(self, symbol: str) -> pd.DataFrame:
        df_prices = self.df_prices.select(lambda x: x == symbol, axis=1)
        if len(df_prices.columns) == 0:
            df_prices = self.df_prices.select(lambda x: x == HeaderFactory.Price, axis=1)
        df_prices.columns = [HeaderFactory.Price]
        df_prices = df_prices.join(self.df_prices[HeaderFactory.Index])
        selected = self.df_prices.select(lambda x: x in HeaderFactory.Columns, axis=1)
        if len(selected.columns) == 0:
            selected = self.df_prices.select(lambda x: x[:-(len(symbol) + 1)] in HeaderFactory.Columns, axis=1)
            selected.rename(columns=lambda x: x[:-(len(symbol) + 1)], inplace=True)
        df_prices = df_prices.join(selected)
        instruction = StrategyDataFactory.construct_instructions(symbol, df_prices)
        return instruction

    @abc.abstractmethod
    def process_buy(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def process_sell(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def process_exit(self, data: pd.DataFrame, instructions: pd.DataFrame) -> pd.DataFrame:
        pass


class BollingerBandStrategy(BaseStrategy):

    def __init__(self, symbols: list, df_prices: pd.DataFrame, stop_loss: StopLossStrategy = None):
        self.bollinger = TechnicalPerformance.compute_bollinger_bands(df_prices)
        super(BollingerBandStrategy, self).__init__(symbols, df_prices, stop_loss)

    def process_buy(self, data: pd.DataFrame) -> pd.DataFrame:
        previous_data = data.shift(1)
        mask = data.loc[(data[HeaderFactory.Bollinger] > -1) & (previous_data[HeaderFactory.Bollinger] <= -1)]
        return mask

    def process_sell(self, data: pd.DataFrame) -> pd.DataFrame:
        previous_data = data.shift(1)
        mask = data.loc[(data[HeaderFactory.Bollinger] < 1) & (previous_data[HeaderFactory.Bollinger] >= 1)]
        return mask

    def process_exit(self, data: pd.DataFrame, instructions: pd.DataFrame) -> pd.DataFrame:
        previous_data = data.shift(1)
        mask = data.loc[((data[HeaderFactory.SMA] >= 0) & (previous_data[HeaderFactory.SMA] < 0)) |
                               ((data[HeaderFactory.SMA] <= 0) & (previous_data[HeaderFactory.SMA] > 0))]
        return mask

    def setup_data(self, symbol: str) -> pd.DataFrame:
        instruction = super(BollingerBandStrategy, self).setup_data(symbol)
        rm = self.bollinger[HeaderFactory.get_name(symbol, HeaderFactory.SMA)]
        rstd = self.bollinger[HeaderFactory.get_name(symbol, HeaderFactory.RSTD)]

        instruction[HeaderFactory.Bollinger] = (instruction[HeaderFactory.Price] - rm) / (2 * rstd)
        instruction[HeaderFactory.SMA] = (instruction[HeaderFactory.Price] / rm) - 1
        return instruction


class MACDBollingerBandStrategy(BollingerBandStrategy):

    def __init__(self, symbols: list, df_prices: pd.DataFrame, stop_loss: StopLossStrategy = None):
        self.macd = TechnicalPerformance.compute_macd(df_prices[symbols])
        super(MACDBollingerBandStrategy, self).__init__(symbols, df_prices, stop_loss)

    def setup_data(self, symbol: str) -> pd.DataFrame:
        instruction = super(MACDBollingerBandStrategy, self).setup_data(symbol)
        instruction[HeaderFactory.MACD] = self.macd[HeaderFactory.get_name(symbol, HeaderFactory.MACD)]
        instruction[HeaderFactory.MACD_SIGNAL] = self.macd[HeaderFactory.get_name(symbol, HeaderFactory.MACD_SIGNAL)]
        instruction[HeaderFactory.MACD_DIFF] = instruction[HeaderFactory.MACD] - instruction[HeaderFactory.MACD_SIGNAL]
        return instruction

    def process_exit(self, base_data: pd.DataFrame, instructions: pd.DataFrame):
        instructions_base = super(MACDBollingerBandStrategy, self).process_exit(base_data, instructions)
        data = base_data.copy()
        data.loc[instructions_base.index, HeaderFactory.Order] = HeaderFactory.EXIT
        previous_data = data.shift(1)
        mask = data.loc[(previous_data[HeaderFactory.MACD_DIFF] > 0) & (data[HeaderFactory.MACD_DIFF] <= 0) &
                        (pd.isnull(data[HeaderFactory.Order]))]

        data.loc[mask.index, HeaderFactory.Order] = HeaderFactory.EXIT

        previous_data = data.shift(1)
        mask = data.loc[(previous_data[HeaderFactory.MACD_DIFF] < 0) & (data[HeaderFactory.MACD_DIFF] >= 0) &
                        (pd.isnull(data[HeaderFactory.Order]))]

        data.loc[mask.index, HeaderFactory.Order] = HeaderFactory.EXIT
        return data.dropna()








