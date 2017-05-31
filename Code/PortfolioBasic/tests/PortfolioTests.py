import unittest
from datetime import datetime
from testfixtures import ShouldRaise
from PortfolioBasic.Portfolio import PortfolioAllocations, PortfolioOrdersFactory


class PortfolioAllocationsTests(unittest.TestCase):

    # preparing to test
    def setUp(self):
        self.symbol_list = ["JAVA", "FAKE1", "FAKE2"]  # list of symbols
        self.allocations = [0.4, 0.2, 0.4]
        self.value = 1000000
        self.start_date = datetime(2005, 12, 31)
        self.end_date = datetime(2014, 12, 7)

    def test_construct(self):
        portfolio = PortfolioAllocations(self.symbol_list, self.allocations, self.start_date, self.end_date, self.value)
        self.assertEquals(1687, len(portfolio.df_data))

    def test_construct_invalid(self):
        with ShouldRaise(ValueError("Mistmatch arrays")):
            portfolio = PortfolioAllocations(self.symbol_list, [0.1, 0.1], self.start_date, self.end_date, self.value)
        with ShouldRaise(ValueError("Unknown <Test> symbol")):
            portfolio = PortfolioAllocations(["Test"], [1], self.start_date, self.end_date, self.value)


class PortfolioOrdersFactoryTests(unittest.TestCase):

    def test_load(self):
        portfolio = PortfolioOrdersFactory.load("..\ml4t\mc2p1\orders-01.csv")
        self.assertEquals(1000000, portfolio.start_val)
        self.assertEquals(4, len(portfolio.symbols))


class PortfolioOrdersTests(unittest.TestCase):

    def setUp(self):
        self.portfolio = PortfolioOrdersFactory.load("..\ml4t\mc2p1\orders-01.csv")

    def test_get_portfolio(self):
        self.portfolio


if __name__ == '__main__':
    unittest.main()
