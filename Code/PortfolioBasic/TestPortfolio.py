"""Fill missing values"""
import logging
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import scale
from sklearn.preprocessing import StandardScaler
from PortfolioBasic.Definitions import HeaderFactory
from PortfolioBasic.MachineLearning.SimpleAlgoTrader import LinearAlgoTrader
from PortfolioBasic.Market.Interactive import IBDataCollector
from PortfolioBasic.Market.MarketDataService import YahooMarketDataSource
from PortfolioBasic.Portfolio import Portfolio, PortfolioAllocations, PortfolioOrders
from PortfolioBasic.Strategy.BasicStrategies import StrategyManager, MACDBollingerBandStrategy
from PortfolioBasic.Strategy.MachineStrategy import MachineStrategyManager
from PortfolioBasic.Strategy.StopLossStrategies import ATRStopLossStrategy
from PortfolioBasic.Technical.Analysis import PortfolioAnalyser, PortfolioPerformance
from PortfolioBasic.Technical.Indicators import CombinedIndicator, MomentumIndicator, BollingerIndicator, RsiIndicator, \
    MACDIndicator
from ib.ext.Contract import Contract

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def plot_data(my_performance: Portfolio, optimized_performance: Portfolio):
    """Plot stock data with appropriate axis labels."""
    # ax = portfolio.df_data.plot(title="Stock Data", fontsize=2)
    ax = my_performance.cumulative_returns.plot(title="Cumulative Returns", label="My ", fontsize=2)
    optimized_performance.cumulative_returns.plot(label="Optimized", fontsize=2, ax=ax)

    spy_data = my_performance.portfolio.df_data["Index"]
    spy_cumulative = (spy_data / spy_data[0]) - 1
    spy_cumulative.plot(fontsize=2, ax=ax)
    # analysis.lower_band.plot(title="Lower Band", fontsize=2, ax=ax)
    # analysis.upper_band.plot(title="Upper Band", fontsize=2, ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.legend(loc='upper left')
    plt.show()


def test_allocations():
    """Function called by Test Run."""
    # Read data
    Portfolio.resources = YahooMarketDataSource()
    PortfolioAnalyser.interest_rate = 0.015

    symbol_list = ['BARC.L', 'RY', 'AZNCF', 'GSK', 'XS7R.L', 'HMWO.L',
                   'SEMB.L', 'MVUS.L', 'CSPX.L', 'CU01.L', 'RDSB.L', 'VOW.DE', 'GLD',
                   'IEUX.L', 'IDBT.L', 'IGWD.L', 'GHYS.L', 'IDEE.L', 'SPMV.L', 'IDWP.L', 'XRMU.L']

    allocations = [0.041676025, 0.129472164, 0.068242756, 0.137921195, 0.049521311, 0.03934012, 0.036098429,
                   0.133767269, 0.036989216, 0.170528155, 0.02400046, 0.017416623, 0.115026277,
                   0, 0, 0, 0, 0, 0, 0, 0]

    allocations[-1] += 1 - np.sum(allocations)
    value = 500000

    start_date = datetime(2016, 1, 1)
    end_date = datetime(2016, 7, 27)
    portfolio_my = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)
    portfolio_optimized = PortfolioAllocations(symbol_list, allocations, start_date, end_date, value)
    my_performance = PortfolioAnalyser.assess_portfolio(portfolio_my)
    PortfolioAnalyser.optimize_portfolio(portfolio_optimized)
    optimized_performance = PortfolioAnalyser.assess_portfolio(portfolio_optimized)

    logging.info("From %s to To %s", my_performance.portfolio.start_date.strftime('%Y-%m-%d'),
                 my_performance.portfolio.end_date.strftime('%Y-%m-%d'))
    logging.info("Cumulative return My: %10.4f Optimized: %10.4f", my_performance.cumulative_return,
                 optimized_performance.cumulative_return)
    logging.info("Sharp Ratio My: %10.4f Optimized: %10.4f", my_performance.sharpe_ratio,
                 optimized_performance.sharpe_ratio)
    logging.info("-------------------")
    for i in range(0, len(optimized_performance.portfolio.allocations)):
        logging.info("Stock %s Now: %10.4f Optimized: %10.4f", optimized_performance.portfolio.symbols[i],
                     my_performance.portfolio.allocations[i], optimized_performance.portfolio.allocations[i])

    # Plot
    plot_data(my_performance, optimized_performance)


def test_ML4T():
    indicators = CombinedIndicator((MomentumIndicator(), BollingerIndicator(), RsiIndicator()))
    algo = LinearAlgoTrader(indicators)
    symbol = 'ML4T-220'
    manager = MachineStrategyManager(symbol, algo)
    start_date = datetime(2007, 12, 31)
    end_date = datetime(2009, 12, 31)
    df_prices = PortfolioOrders.resources.get_data([symbol], start_date, end_date, True)
    manager.train_strategy(start_date, end_date)
    result, rmse, c = manager.algo.predict(df_prices)
    ax = result.plot(title="Predicted", label="My ", fontsize=2)
    data = df_prices.Price
    y_data = data.shift(-5) / data - 1.0
    y_data.plot(label="Actual", fontsize=2, ax=ax)
    plt.legend(loc='upper left')
    plt.show()


def test_real_machine():
    Portfolio.resources = YahooMarketDataSource()
    PortfolioAnalyser.interest_rate = 0.015
    indicators = CombinedIndicator((MomentumIndicator(), BollingerIndicator(), RsiIndicator(), MACDIndicator()))

    symbol_list = ['RY', 'AZNCF', 'GSK', 'GLD']
    symbol_list = ['EZJ.L']
    symbol_list = ['CS']

    for symbol in symbol_list:
        algo = LinearAlgoTrader(indicators, dump=True)
        manager = MachineStrategyManager(symbol, algo)
        start_date = datetime(2014, 12, 31)
        end_date = datetime(2016, 3, 31)
        manager.train_strategy(start_date, end_date)

        start_date = datetime(2016, 4, 1)
        end_date = datetime(2016, 7, 28)
        df_prices = PortfolioOrders.resources.get_data(["SPY"], start_date, end_date, True)
        instructions = manager.process_strategy(start_date, end_date, threshold=0.01)

        portfolio = PortfolioOrders(instructions, 10000)
        analysis = PortfolioAnalyser.assess_portfolio(portfolio)

        plot_performance(analysis, df_prices)


def test_strategy_basic_run():
    symbols = ["IBM", "GE"]
    start_date = datetime(2007, 12, 31)
    end_date = datetime(2012, 12, 31)
    PortfolioAnalyser.interest_rate = 0
    analyse_strategy(MACDBollingerBandStrategy, symbols, start_date, end_date)


def test_strategy_run():
    Portfolio.resources = YahooMarketDataSource()
    PortfolioAnalyser.interest_rate = 0.015
    symbols = ['BCS', 'RY', 'AZNCF', 'GSK', 'VOW.DE', 'GLD']

    start_date = datetime(2014, 6, 1)
    end_date = datetime(2016, 6, 25)
    analyse_strategy(MACDBollingerBandStrategy, symbols, start_date, end_date)


def analyse_strategy(Class, symbols, start_date, end_date):
    strategy = StrategyManager(symbols, start_date, end_date)
    strategy.process_strategy(Class)
    strategy.instruction.to_csv("instructions.csv", index_label="Date")
    portfolio = PortfolioOrders(strategy.instruction, 10000)
    analysis = PortfolioAnalyser.assess_portfolio(portfolio)
    plot_performance(analysis, strategy.df_prices)


def plot_performance(analysis: PortfolioPerformance, index: pd.DataFrame):
    logging.info("Cumulitive: %s", analysis.cumulative_return)
    ax = analysis.cumulative_returns.plot(title="Cumulative Returns", label="My ", fontsize=2)
    spy_data = index[HeaderFactory.Index]
    spy_cumulative = (spy_data / spy_data[0]) - 1
    spy_cumulative.plot(fontsize=2, ax=ax)
    # analysis.lower_band.plot(title="Lower Band", fontsize=2, ax=ax)
    # analysis.upper_band.plot(title="Upper Band", fontsize=2, ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.legend(loc='upper left')
    plt.show()

if __name__ == "__main__":
    # test_allocations()
    # test_real_machine()
    # https://www.interactivebrokers.co.uk/en/software/api/apiguide/java/contract.htm
    contract = Contract()
    contract.m_symbol = "B"
    contract.m_secType = 'STK'
    contract.m_exchange = "Nasdaq"
    contract.m_currency = 'USD'
    prev_date = '%04d%02d%02d' % (2016, 7, 22)
    h = '20'
    broker = IBDataCollector(contract, prev_date, '20:00:00', 7200)
    broker.close()
