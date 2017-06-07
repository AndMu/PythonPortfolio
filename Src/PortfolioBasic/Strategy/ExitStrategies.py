import abc

import pandas as pd

from PortfolioBasic.Definitions import HeaderFactory
from PortfolioBasic.Strategy.StopLossStrategies import StopLossStrategy


class ExitStrategy(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, stop_loss: StopLossStrategy):
        self.stop_loss = stop_loss

    @abc.abstractmethod
    def process_exit(self, data: pd.DataFrame) -> pd.DataFrame:
        pass


class DayExitStrategy(ExitStrategy):

    def __init__(self, days: int, stop_loss: StopLossStrategy):
        self.days = days
        if stop_loss is None:
            raise ValueError("Please add stop loss")
        super(DayExitStrategy, self).__init__(stop_loss)

    def process_exit(self, instructions: pd.DataFrame) -> pd.DataFrame:
        mask = instructions.loc[(instructions[HeaderFactory.Order] == HeaderFactory.BUY) |
                                (instructions[HeaderFactory.Order] == HeaderFactory.SELL)]

        action = None
        exit_date = None
        # current.timedelta(days=-self.days):
        for date in mask.index:
            new_order = False
            loc = instructions.index.get_loc(date)
            index = self.days + loc
            if index < len(instructions.index):
                possible_exit_date = instructions.index[index]
            else:
                possible_exit_date = None

            if exit_date is not None and exit_date < date:
                instructions.loc[exit_date, HeaderFactory.Order] = self._get_exit(action)
                action = None

            current = instructions.loc[date, HeaderFactory.Order]
            if current == action or action is None:
                if action is not None:
                    instructions.loc[date, HeaderFactory.Order] = None
                else:
                    new_order = True

                exit_date = possible_exit_date
                action = current
            else:
                new_order = True
                instructions.loc[date, HeaderFactory.Shares] *= 2
                exit_date = possible_exit_date
                action = current

            if new_order:
                low, high = self.stop_loss.get_exit(date)
                instructions.loc[date, HeaderFactory.StopLow] = low
                instructions.loc[date, HeaderFactory.StopHigh] = high

            if len(instructions.index) > (loc + 1):
                next_day = instructions.index[loc + 1]
                mask = instructions.loc[(instructions[HeaderFactory.Price] >= high) |
                                        (instructions[HeaderFactory.Price] <= low)].loc[next_day:possible_exit_date]

            if len(mask.index) > 0:
                exit_date = mask.index[0]

        if exit_date is not None:
            instructions.loc[exit_date, HeaderFactory.Order] = self._get_exit(action)

        return instructions.dropna(subset=[HeaderFactory.Order])

    def _get_exit(self, action: str) -> str:
        if action == HeaderFactory.BUY:
            return HeaderFactory.SELL
        return HeaderFactory.BUY
