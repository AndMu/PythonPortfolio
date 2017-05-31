import abc
import math
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import StandardScaler

from PortfolioBasic.Definitions import HeaderFactory
from PortfolioBasic.Technical.Indicators import CombinedIndicator
import numpy as np


class BaseAlgoTrader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, indicators: CombinedIndicator, prediction_days=5):
        self.prediction_days = prediction_days
        self.indicators = indicators

    @abc.abstractmethod
    def train(self, data: pd.DataFrame):
        pass

    @abc.abstractmethod
    def predict(self, data: pd.DataFrame):
        pass


class LinearAlgoTrader(BaseAlgoTrader):
    def __init__(self, indicators: CombinedIndicator, prediction_days=5, dump=False):
        self.dump = dump
        self.regression = linear_model.LinearRegression()
        super(LinearAlgoTrader, self).__init__(indicators, prediction_days)

    def train(self, data: pd.DataFrame):
        x_data_train, y_data_train = self.get_data(data)
        if self.dump:
            x_data_train.join(y_data_train, rsuffix='_Traing').to_csv("testing.csv")

        x_data_train = x_data_train.iloc[:-self.prediction_days, :].values
        y_data_train = y_data_train.iloc[:-self.prediction_days].values
        self.regression.fit(x_data_train, y_data_train)

    def predict(self, data: pd.DataFrame):
        x_data_test, y_data_test = self.get_data(data)
        if self.dump:
            x_data_test.join(y_data_test, rsuffix='_Test').to_csv("testing.csv")

        y_predict = self.regression.predict(x_data_test)
        result = pd.DataFrame(index=x_data_test.index, data=y_predict, columns=[HeaderFactory.MACHINE])

        y_data_test = y_data_test.iloc[:-self.prediction_days].values
        y_predict = y_predict[:-self.prediction_days]
        rmse = math.sqrt(((y_data_test - y_predict) ** 2).sum() / y_data_test.shape[0])
        c = np.corrcoef(y_predict.T, y=y_data_test.T)
        return result, rmse, c[0, 1]

    def get_data(self, data: pd.DataFrame):
        x_data = self.indicators.calculate(data)
        y_data = data.shift(-self.prediction_days) / data - 1.0
        x_data.dropna(inplace=True)
        y_data = y_data.loc[x_data.index, HeaderFactory.Price]
        return x_data, y_data