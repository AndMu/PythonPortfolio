from collections import OrderedDict


class PortfolioTestCase:
    def __init__(self, inputs: dict, outputs: dict, description: str):
        self.inputs = inputs
        self.outputs = outputs
        self.description = description


class PortfolioTestCaseData:
    portfolio_test_cases = [
        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2010-12-31',
                symbol_allocs=OrderedDict([('GOOG', 0.2), ('AAPL', 0.3), ('GLD', 0.4), ('XOM', 0.1)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.255646784534,
                avg_daily_ret=0.000957366234238,
                sharpe_ratio=1.51819243641),
            description="Wiki example 1"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2010-12-31',
                symbol_allocs=OrderedDict([('AXP', 0.0), ('HPQ', 0.0), ('IBM', 0.0), ('HNZ', 1.0)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.198105963655,
                avg_daily_ret=0.000763106152672,
                sharpe_ratio=1.30798398744),
            description="Wiki example 2"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-06-01',
                end_date='2010-12-31',
                symbol_allocs=OrderedDict([('GOOG', 0.2), ('AAPL', 0.3), ('GLD', 0.4), ('XOM', 0.1)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.205113938792,
                avg_daily_ret=0.00129586924366,
                sharpe_ratio=2.21259766672),
            description="Wiki example 3: Six month range"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2010-12-31',
                symbol_allocs=OrderedDict([('GOOG', 0.2), ('AAPL', 0.4), ('GLD', 0.2), ('XOM', 0.2)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.262285147745,
                avg_daily_ret=0.000993303139465,
                sharpe_ratio=1.3812384175),
            description="Wiki example 1 with different allocations"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2013-05-31',
                symbol_allocs=OrderedDict([('AXP', 0.3), ('HPQ', 0.5), ('IBM', 0.1), ('GOOG', 0.1)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=-0.110888530433,
                avg_daily_ret=-6.50814806831e-05,
                sharpe_ratio=-0.0704694718385),
            description="Normalization check"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2010-01-31',
                symbol_allocs=OrderedDict([('AXP', 0.9), ('HPQ', 0.0), ('IBM', 0.1), ('GOOG', 0.0)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=-0.0758725033871,
                avg_daily_ret=-0.00411578300489,
                sharpe_ratio=-2.84503813366),
            description="One month range"

        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2011-01-01',
                end_date='2011-12-31',
                symbol_allocs=OrderedDict([('WFR', 0.25), ('ANR', 0.25), ('MWW', 0.25), ('FSLR', 0.25)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=-0.686004563165,
                avg_daily_ret=-0.00405018240566,
                sharpe_ratio=-1.93664660013),
            description="Low Sharpe ratio"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-01-01',
                end_date='2010-12-31',
                symbol_allocs=OrderedDict([('AXP', 0.0), ('HPQ', 1.0), ('IBM', 0.0), ('HNZ', 0.0)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=-0.191620333598,
                avg_daily_ret=-0.000718040989619,
                sharpe_ratio=-0.71237182415),
            description="All your eggs in one basket"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2010-06-01',
                end_date='2011-06-01',
                symbol_allocs=OrderedDict([('AAPL', 0.1), ('GLD', 0.4), ('GOOG', 0.5), ('XOM', 0.0)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.177352039318,
                avg_daily_ret= 0.000694756409052,
                sharpe_ratio=1.10895144722),
            description="Mid-2010 to mid-2011"
        ),

        PortfolioTestCase(
            inputs=dict(
                start_date='2006-01-03',
                end_date='2008-01-02',
                symbol_allocs=OrderedDict([('MMM', 0.0), ('MO', 0.9), ('MSFT', 0.1), ('INTC', 0.0)]),
                start_val=1000000),
            outputs=dict(
                cum_ret=0.43732715979,
                avg_daily_ret=0.00076948918955,
                sharpe_ratio=1.26449481371),
            description="Two year range"
        )
    ]
