import pandas as pd
import scipy.optimize as spo
import logging
import talib
from PortfolioBasic import Portfolio
from PortfolioBasic.Definitions import HeaderFactory

logger = logging.getLogger(__name__)


class PortfolioPerformance:
    def __init__(self, portfolio: Portfolio, interest_rate=0.01):
        self.portfolio = portfolio
        daily_portfolio_values = portfolio.get_daily_values()
        self.cumulative_returns = (daily_portfolio_values / daily_portfolio_values[0]) - 1
        self.cumulative_return = (daily_portfolio_values[-1] / daily_portfolio_values[0]) - 1
        self.daily_returns = daily_portfolio_values.copy()
        self.daily_returns[1:] = (self.daily_returns[1:] / self.daily_returns[:-1].values) - 1
        self.daily_returns = self.daily_returns[1:]
        self.avg_daily_return = self.daily_returns.mean()
        self.volatility = self.daily_returns.std()
        daily_risk_free = ((1.0 + interest_rate) ** (1. / 252.)) - 1
        adjusted_daily_return = (self.daily_returns - daily_risk_free).mean()
        self.sharpe_ratio = (252 ** (1. / 2.)) * adjusted_daily_return / self.volatility


class PortfolioAnalyser:
    interest_rate = 0.01

    @staticmethod
    def assess_portfolio(portfolio: Portfolio) -> PortfolioPerformance:
        return PortfolioPerformance(portfolio, PortfolioAnalyser.interest_rate)

    @staticmethod
    def optimize_portfolio(portfolio: Portfolio):
        logger.info("Optimizing portfolio")

        bounds = []
        for _ in portfolio.allocations:
            bounds.append((0, 1))

        constrain = ({'type': 'eq', 'fun': lambda x: 1 - sum(x)})
        result = spo.minimize(PortfolioAnalyser.sharpe_function_optimization, portfolio.allocations, args=(portfolio,),
                              method='SLSQP', bounds=bounds, constraints=constrain, options={'disp': True})
        logger.info("Calculated allocations %s", result)
        portfolio.allocations = result.x

    @staticmethod
    def sharpe_function_optimization(allocations, portfolio):
        # error function
        portfolio.allocations = allocations
        return -1 * PortfolioAnalyser.assess_portfolio(portfolio).sharpe_ratio


class TechnicalPerformance:
    @staticmethod
    def compute_std(data: pd.DataFrame, window=20):
        # 1. Compute rolling mean
        rm = data.rolling(center=False, window=window).mean()
        # 2. Compute rolling standard deviation
        rstd = data.rolling(window=window, center=False).std()
        return rm, rstd

    @staticmethod
    def compute_adr(data: pd.DataFrame, period=7):
        difference = data["High"] - data["Low"]
        return difference.rolling(window=period, center=False).mean()

    @staticmethod
    def estimateBeta(algo_price: pd.DataFrame, benchmark_price: pd.DataFrame):
        algorithm_returns = (algo_price / algo_price.shift(1) - 1).dropna().values
        benchmark_returns = (benchmark_price / benchmark_price.shift(1) - 1).dropna().values
        if len(algorithm_returns) != len(benchmark_returns):
            minlen = min(len(algorithm_returns), len(benchmark_returns))
            if minlen > 2:
                algorithm_returns = algorithm_returns[-minlen:]
                benchmark_returns = benchmark_returns[-minlen:]
            else:
                return 1.00
        returns_matrix = pd.np.vstack([algorithm_returns, benchmark_returns])
        C = pd.np.cov(returns_matrix, ddof=1)
        algorithm_covariance = C[0][1]
        benchmark_variance = C[1][1]
        beta = algorithm_covariance / benchmark_variance
        return beta

    @staticmethod
    def compute_macd(data: pd.DataFrame, n_fast=12, n_slow=26, signal_period=9) -> pd.DataFrame:
        '''
            Function to return the difference between the most recent
            MACD value and MACD signal. Positive values are long
            position entry signals

            optional args:
                n_fast = 12
                n_slow =
                 26
                signal_period = 9
            Returns: panda macd
            '''

        macd = data.apply(TechnicalPerformance._MACD, fastperiod=n_fast, slowperiod=n_slow, signalperiod=signal_period)
        macd = macd.unstack().reset_index()
        if len(macd['level_0']) > 0:
            macd['level_0'] = macd['level_0'] + '_' + macd['level_1']
        else:
            macd['level_0'] = macd['level_1']
        macd = macd.drop('level_1', axis=1)
        raw_data = macd[0].apply(lambda x: pd.Series(x))
        macd = macd.drop(0, axis=1).join(raw_data).transpose().reset_index()
        macd.columns = macd.iloc[0]
        macd = macd.drop('level_0', axis=1)
        result = pd.DataFrame(index=data.index, data=macd.iloc[1:].values, columns=macd.columns)
        return result

    # Define the MACD function
    @staticmethod
    def _MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9):
        '''
        Function to return the difference between the most recent
        MACD value and MACD signal. Positive values are long
        position entry signals

        optional args:
            fastperiod = 12
            slowperiod = 26
            signalperiod = 9

        Returns: macd - signal
        '''
        macd, signal, hist = talib.MACD(prices.values,
                                        fastperiod=fastperiod,
                                        slowperiod=slowperiod,
                                        signalperiod=signalperiod)

        return pd.Series({HeaderFactory.MACD: macd, HeaderFactory.MACD_SIGNAL: signal, HeaderFactory.MACD_HIST: hist})

    @staticmethod
    def compute_bollinger_bands(data: pd.DataFrame, window=20, deviation=2):
        # Compute Bollinger Bands
        # 1. Compute rolling mean

        rm, rstd = TechnicalPerformance.compute_std(data, window)
        # 3. Compute upper and lower bands
        upper_band, lower_band = TechnicalPerformance.get_bollinger_bands(rm, rstd, deviation)
        rm.columns = HeaderFactory.get_name(rm.columns, HeaderFactory.SMA)
        rstd.columns = HeaderFactory.get_name(rstd.columns, HeaderFactory.RSTD)
        upper_band.columns = HeaderFactory.get_name(upper_band.columns, HeaderFactory.BB_UPPER_BAND)
        lower_band.columns = HeaderFactory.get_name(lower_band.columns, HeaderFactory.BB_LOWER_BAND)
        data = data.join(rm)
        data = data.join(rstd)
        data = data.join(lower_band)
        data = data.join(upper_band)
        return data

    @staticmethod
    def get_rolling_mean(values, window):
        """Return rolling mean of given values, using specified window size."""
        return pd.rolling_mean(values, window=window)

    @staticmethod
    def get_rolling_std(values, window):
        """Return rolling standard deviation of given values, using specified window size."""
        return pd.rolling_std(values, window=window)

    @staticmethod
    def get_bollinger_bands(rm, rstd, deviation=2):
        """Return upper and lower Bollinger Bands."""
        upper_band = rm + rstd * deviation
        lower_band = rm - rstd * deviation
        return upper_band, lower_band

