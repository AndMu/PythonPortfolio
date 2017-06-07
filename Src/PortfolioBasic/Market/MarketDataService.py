import os
from datetime import datetime
from os import listdir
from os.path import isfile, join
import abc
import numpy as np
import pandas as pd
import logging

import shutil
from yahoo_finance import Share

from PortfolioBasic.Definitions import HeaderFactory

logger = logging.getLogger(__name__)


class MarketDataSource(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_stock_data(self, symbol: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        """Get stock data frame"""
        return None

    @abc.abstractmethod
    def can_use(self, symbol):
        return False

    def get_index(self, symbols: list):
        return "SPY"

    def get_data(self, symbols: list, start_date: datetime, end_date: datetime, use_single=False):

        symbols = symbols.copy()
        dates = pd.date_range(start_date, end_date)  # date range as index
        df_final = pd.DataFrame(index=dates)
        index = self.get_index(symbols)
        if index not in symbols:  # add SPY for reference, if absent
            symbols.insert(0, index)

        for symbol in symbols:
            logging.info("Requesting stock information %s from %s to %s...", symbol, start_date, end_date)
            df_temp = self.get_stock_data(symbol, start_date, end_date)

            if symbol == index:  # in case of index take only index value
                df_temp = df_temp[index]
                df_temp.name = HeaderFactory.Index
                df_temp = pd.DataFrame(df_temp)
            else:
                if not use_single:
                    df_temp.rename(columns=lambda x: x + '_' + symbol if x in HeaderFactory.Columns else x,
                                   inplace=True)
                else:
                    df_temp.rename(columns={symbol: HeaderFactory.Price}, inplace=True)

            df_final = df_final.join(df_temp)
            if symbol == index:  # drop dates SPY did not trade
                df_final = df_final.dropna(subset=[HeaderFactory.Index])

        return df_final


class LocalMarketDataSource(MarketDataSource):

    def can_use(self, symbol):
        return symbol in self.indexes

    def __init__(self, base_dir="..\ml4t\data"):
        self.base_dir = base_dir
        self.indexes = [os.path.splitext(file_name)[0] for file_name in listdir(base_dir) if isfile(join(base_dir,
                                                                                                         file_name))]

    def get_stock_data(self, symbol: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        file_path = self.symbol_to_path(symbol)
        columns = ["Date", "Adj Close", "Open", "High", "Low", "Close", "Volume"]
        df_temp = pd.read_csv(file_path, parse_dates=True, index_col="Date", usecols=columns, na_values=["nan"])
        df_temp = df_temp.rename(columns={"Adj Close": symbol})
        return df_temp

    def symbol_to_path(self, symbol):
        """Return CSV file path given ticker symbol."""
        return os.path.join(self.base_dir, "{}.csv".format(str(symbol)))


class YahooMarketDataSource(MarketDataSource):

    def __init__(self, base_dir="..\cache\data"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def reset_cache(self):
        shutil.rmtree(self.base_dir)
        os.makedirs(self.base_dir)

    def can_use(self, symbol):
        return True

    def get_stock_data(self, symbol: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        filename = "{}-{}-{}.csv".format(str(symbol), from_date.strftime('%Y%m%d'), to_date.strftime('%Y%m%d'))
        filename = os.path.join(self.base_dir, filename)
        if os.path.isfile(filename):
            return pd.read_csv(filename, parse_dates=True, index_col="Date", na_values=["nan"])
        share = Share(symbol)
        from_date_str = from_date.strftime('%Y-%m-%d')
        to_date_str = to_date.strftime('%Y-%m-%d')
        data = share.get_historical(from_date_str, to_date_str)
        data_frame = pd.DataFrame(data, dtype=np.float32)
        columns = ["Date", "Adj_Close", "Open", "High", "Low", "Close", "Volume"]
        data_frame = data_frame[columns]
        data_frame = data_frame.set_index(['Date'])
        data_frame = data_frame.rename(columns={"Adj_Close": symbol})
        data_frame.to_csv(filename)
        return data_frame
