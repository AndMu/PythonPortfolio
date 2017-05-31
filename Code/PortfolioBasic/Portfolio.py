import abc
import logging
import os.path
from datetime import datetime
import numpy as np
import pandas as pd

from PortfolioBasic.Definitions import Utilities
from PortfolioBasic.Market.MarketDataService import LocalMarketDataSource
logger = logging.getLogger(__name__)


class Portfolio(object):
    resources = LocalMarketDataSource()
    __metaclass__ = abc.ABCMeta

    def __init__(self, symbols: list, start_date: datetime, end_date: datetime):
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date

    @abc.abstractmethod
    def get_daily_values(self) -> pd.DataFrame:
        """Get stock data frame"""
        return None


class PortfolioOrders(Portfolio):

    def __init__(self, orders: pd.DataFrame, start_val: float, end_date: datetime = None):
        self.start_val = start_val
        symbols = orders.Symbol.unique()
        orders['Shares'] = orders.Shares.where(orders.Order == 'BUY', other=-orders.Shares)
        if end_date is None:
            end_date = orders.index[-1]
        start_date = orders.index[0]
        super().__init__(symbols, start_date, end_date)
        self.df_prices = PortfolioOrders.resources.get_data(self.symbols.tolist(), start_date, end_date)
        self.orders = orders
        df_trades = orders.reset_index().groupby(['Date', 'Symbol']).sum().reset_index()
        df_trades = df_trades.pivot(index='Date', columns='Symbol', values='Shares')
        df_trades.fillna(value=0, inplace=True)
        idx = pd.date_range(start_date, end_date)
        df_trades = df_trades.reindex(idx, fill_value=0)
        df_positions = self.df_prices * df_trades
        df_holdings = df_trades.copy()

        df_positions['Total'] = df_positions.sum(axis=1)
        df_holdings.loc[df_positions.index, 'Total'] = df_positions.Total
        df_holdings = df_holdings.cumsum()
        df_holdings['Cash'] = start_val - df_holdings['Total']
        df_holdings.fillna(method='ffill', inplace=True)
        self.df_value = df_holdings[self.symbols] * self.df_prices[self.symbols]
        self.df_value = self.df_value.dropna()
        self.df_value["Cash"] = df_holdings['Cash']
        self.daily_portfolio_values = self.df_value.sum(axis=1)
        self.df_value["Leverage"] = self.df_value[self.symbols].abs().sum(axis=1) / (self.df_value[self.symbols]
                                                                                     .sum(axis=1) + self.df_value.Cash)
        pass

    def is_over_leveraged(self, max_leverage=2):
        return self.df_value["Leverage"].max() > max_leverage

    def get_daily_values(self) -> pd.DataFrame:
        return self.daily_portfolio_values


class PortfolioOrdersLeverageManager:
    @staticmethod
    def deleverage(portfolio: PortfolioOrders, max_leverage=2):
        while portfolio.is_over_leveraged(max_leverage):
            develeveraged = PortfolioOrdersLeverageManager.deleverage_once(portfolio, max_leverage)
            if develeveraged is None:
                logger.warn("Failed to deleverage")
                return portfolio
            else:
                portfolio = develeveraged
        return portfolio

    @staticmethod
    def deleverage_once(portfolio: PortfolioOrders, max_leverage=2):
        orders = portfolio.orders
        orders["Leverage"] = portfolio.df_value.Leverage
        orders = orders.reset_index()
        locations = orders.loc[orders['Leverage'] > max_leverage]
        if len(locations) == 0:
            return None
        orders.drop(locations.index[0], inplace=True)
        orders = orders.set_index(["Date"])
        orders.drop('Leverage', axis=1, inplace=True)
        orders["Shares"] = orders.Shares.abs()
        return PortfolioOrders(orders, portfolio.start_val, portfolio.end_date)


class PortfolioOrdersFactory:
    @staticmethod
    def load(filename: str, start_val=1000000, end_date: datetime = None) -> PortfolioOrders:
        if not os.path.isfile(filename):
            raise ValueError("Can't find <{}> file".format(filename))

        data = pd.read_csv(filename, parse_dates=True, index_col="Date", na_values=["nan"])
        return PortfolioOrders(data, start_val, end_date)


class PortfolioAllocations(Portfolio):

    def __init__(self, symbols: list, allocations: np.array, start_date: datetime, end_date: datetime, value):
        super().__init__(symbols, start_date, end_date)
        self.start_date = start_date
        self.end_date = end_date
        self.value = value
        self.df_data = pd.DataFrame()

        for symbol in symbols:
            if not Portfolio.resources.can_use(symbol):
                raise ValueError("Unknown <{}> symbol".format(symbol))

        if len(symbols) != len(allocations):
            raise ValueError("Mistmatch arrays")

        self.allocations = allocations
        self.fill_data()

    def get_daily_values(self):
        normalized_returns = self.df_data / self.df_data.ix[0, :]
        daily_portfolio_values = (normalized_returns[self.symbols] * self.allocations * self.value).sum(axis=1)
        return daily_portfolio_values

    def fill_data(self):
        # get data for each symbol
        self.df_data = Portfolio.resources.get_data(self.symbols.copy(), self.start_date, self.end_date)
        Utilities.fill_missing_values(self.df_data)


