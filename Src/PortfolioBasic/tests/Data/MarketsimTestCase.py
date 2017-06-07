class MarketsimTestCase:
    def __init__(self, inputs: dict, outputs: dict, description: str, group: str):
        self.inputs = inputs
        self.group = group
        self.outputs = outputs
        self.description = description


class MarketsimTestCaseData:
    marketsim_test_cases = [
        MarketsimTestCase(
            description="Orders 1",
            group='basic',
            inputs=dict(
                orders_file='orders-01.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=245,
                last_day_portval=1115569.2,
                sharpe_ratio=0.612340613407,
                avg_daily_ret=0.00055037432146
            )
        ),
        MarketsimTestCase(
            description="Orders 2",
            group='basic',
            inputs=dict(
                orders_file='orders-02.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=245,
                last_day_portval=1095003.35,
                sharpe_ratio=1.01613520942,
                avg_daily_ret=0.000390534819609
            )
        ),
        MarketsimTestCase(
            description="Orders 3",
            group='basic',
            inputs=dict(
                orders_file='orders-03.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=240,
                last_day_portval=857616.0,
                sharpe_ratio=-0.759896272199,
                avg_daily_ret=-0.000571326189931
            )
        ),
        MarketsimTestCase(
            description="Orders 4",
            group='basic',
            inputs=dict(
                orders_file='orders-04.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=233,
                last_day_portval=923545.4,
                sharpe_ratio=-0.266030146916,
                avg_daily_ret=-0.000240200768212
            )
        ),
        MarketsimTestCase(
            description="Orders 5",
            group='basic',
            inputs=dict(
                orders_file='orders-05.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=296,
                last_day_portval=1415563.0,
                sharpe_ratio=2.19591520826,
                avg_daily_ret=0.00121733290744
            )
        ),
        MarketsimTestCase(
            description="Orders 6",
            group='basic',
            inputs=dict(
                orders_file='orders-06.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=210,
                last_day_portval=894604.3,
                sharpe_ratio=-1.23463930987,
                avg_daily_ret=-0.000511281541086
            )
        ),
        MarketsimTestCase(
            description="Orders 7 (modified)",
            group='basic',
            inputs=dict(
                orders_file='orders-07-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=237,
                last_day_portval=1104930.8,
                sharpe_ratio=2.07335994413,
                avg_daily_ret=0.000428245010481
            )
        ),
        MarketsimTestCase(
            description="Orders 8 (modified)",
            group='basic',
            inputs=dict(
                orders_file='orders-08-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=229,
                last_day_portval=1071325.1,
                sharpe_ratio=0.896734443277,
                avg_daily_ret=0.000318004442115
            )
        ),
        MarketsimTestCase(
            description="Orders 9 (modified)",
            group='basic',
            inputs=dict(
                orders_file='orders-09-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=37,
                last_day_portval=1058990.0,
                sharpe_ratio=2.54864656282,
                avg_daily_ret=0.00164458341408
            )
        ),
        MarketsimTestCase(
            description="Orders 10 (modified)",
            group='basic',
            inputs=dict(
                orders_file='orders-10-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                num_days=141,
                last_day_portval=1070819.0,
                sharpe_ratio=1.0145855303,
                avg_daily_ret=0.000521814978394
            )
        ),
        MarketsimTestCase(
            description="Orders 11 - Leveraged SELL (modified)",
            group='leverage',
            inputs=dict(
                orders_file='orders-11-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                last_day_portval=1053560.0
            )
        ),
        MarketsimTestCase(
            description="Orders 12 - Leveraged BUY (modified)",
            group='leverage',
            inputs=dict(
                orders_file='orders-12-modified.csv',
                start_val=1000000
            ),
            outputs=dict(
                last_day_portval=1044437.0
            )
        ),
        MarketsimTestCase(
            description="Wiki leverage example #1",
            group='leverage',
            inputs=dict(
                orders_file='orders-leverage-1.csv',
                start_val=1000000
            ),
            outputs=dict(
                last_day_portval=1050160.0
            )
        ),
        MarketsimTestCase(
            description="Wiki leverage example #2",
            group='leverage',
            inputs=dict(
                orders_file='orders-leverage-2.csv',
                start_val=1000000
            ),
            outputs=dict(
                last_day_portval=1074650.0
            )
        ),
        MarketsimTestCase(
            description="Wiki leverage example #3",
            group='leverage',
            inputs=dict(
                orders_file='orders-leverage-3.csv',
                start_val=1000000
            ),
            outputs=dict(
                last_day_portval=1050160.0
            )
        ),
    ]
