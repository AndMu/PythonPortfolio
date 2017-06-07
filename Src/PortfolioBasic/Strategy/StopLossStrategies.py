import abc
import datetime

import pandas as pd

from PortfolioBasic.Technical.Analysis import HeaderFactory, TechnicalPerformance


class StopLossStrategy(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def pre_process(self, data: pd.DataFrame):
        pass

    @abc.abstractmethod
    def get_exit(self, date: datetime, short=False):
        pass

    @abc.abstractmethod
    def process(self, original_data: pd.DataFrame, instruction_original: pd.DataFrame) -> pd.DataFrame:
        pass


class ATRStopLossStrategy(StopLossStrategy):

    def __init__(self, low=2, high=3):
        self.low = low
        self.high = high
        self.data = None

    def pre_process(self, data: pd.DataFrame):
        adr = TechnicalPerformance.compute_adr(data)
        self.data = data.copy()
        self.data[HeaderFactory.ADR] = adr

    def get_exit(self, date: datetime, short=False):
        if not short:
            low = self.data.loc[date, HeaderFactory.Price] - self.low * self.data.loc[date, HeaderFactory.ADR]
            high = self.data.loc[date, HeaderFactory.Price] + self.high * self.data.loc[date, HeaderFactory.ADR]
        else:
            high = self.data.loc[date, HeaderFactory.Price] + self.low * self.data.loc[date, HeaderFactory.ADR]
            low = self.data.loc[date, HeaderFactory.Price] - self.high * self.data.loc[date, HeaderFactory.ADR]

        return low, high

    def process(self, original_data: pd.DataFrame, instruction_original: pd.DataFrame) -> pd.DataFrame:

        self.pre_process(original_data)
        data = self.data
        data.loc[instruction_original.index, HeaderFactory.Order] = instruction_original[HeaderFactory.Order]
        original_instruction_full = data.copy()

        mask = data.loc[data[HeaderFactory.Order] == HeaderFactory.BUY]
        filtered = data.loc[mask.index]
        data.loc[mask.index, HeaderFactory.StopLow] = filtered[HeaderFactory.Low] - \
                                                 (self.low * filtered[HeaderFactory.ADR])
        data.loc[mask.index, HeaderFactory.StopHigh] = filtered[HeaderFactory.High] + \
                                                 (self.high * filtered[HeaderFactory.ADR])

        mask = data.loc[data[HeaderFactory.Order] == HeaderFactory.SELL]
        filtered = data.loc[mask.index]
        ''' In cased of short we have inverted '''
        data.loc[mask.index, "StopTop"] = filtered[HeaderFactory.High] + \
                                                 (self.low * filtered[HeaderFactory.ADR])
        data.loc[mask.index, "StopLow"] = filtered[HeaderFactory.Low] - \
                                                 (self.high * filtered[HeaderFactory.ADR])
        data[HeaderFactory.StopHigh].fillna(method='ffill', inplace=True)
        data[HeaderFactory.StopLow].fillna(method='ffill', inplace=True)
        mask = data.loc[(data[HeaderFactory.Price] >= data[HeaderFactory.StopHigh]) |
                        (data[HeaderFactory.Price] <= data[HeaderFactory.StopLow])]
        # original_instruction_full.to_csv("instruction_pre.csv")
        original_instruction_full.loc[mask.index, HeaderFactory.Order] = HeaderFactory.EXIT
        # original_instruction_full.to_csv("instruction.csv")
        return original_instruction_full
