import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyfolio as pf
import csv; import datetime; import pytz
from technical_indicators import BBANDS
from historical_data import exchange_data,write_to_csv,to_unix_time
import backtest
import warnings
warnings.filterwarnings('ignore')

# ==========Initial trade parameters =============
symbol = 'BTC/USD'
timeframe = '5m'
trading_qty = 1.0
since = '2017-01-01 00:00:00'
hist_start_date = int(to_unix_time(since))
header = ['Timestamp', 'Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume']
period = []
trn_cost = 0.001

# ==========Initial exchange parameters =============
# kraken = exchange_data('kraken', 'BTC/USD', timeframe=timeframe, since=hist_start_date)
# write_to_csv(kraken,'BTC/USD','kraken')

# data = pd.DataFrame(kraken, columns=header)
# print(data.head())
data = pd.read_csv("gemini_BTCUSD_1hr.csv" )

def ema(data,period):
    ema = data['Close'].ewm(span=period, adjust=False).mean()
    return ema

# ============ Strategy Function - Exponential Moving average crossover ================
def strategy(data):
    for period in range(20,100,5):
        ema_short = ema(data,period)

        # Difference between prices & EMA timeseries
        trading_positions_raw = data['Close'] - ema_short
        #trading_positions_raw.tail()

        # Taking the sign of the difference to determine whether the price or EMA is greater and then
        # multiply by qty

        trading_positions = trading_positions_raw.apply(np.sign)
        print('Trading Positions:', trading_positions.head())

        data['trad_posn_chg'] = trading_positions.shift(1) - trading_positions

        data['trn_cost'] = 0
        for trd in range(len(data)):
            if data['trad_posn_chg'].iloc[trd] == 2 or data['trad_posn_chg'].iloc[trd] == -2:
                data['trn_cost'].iloc[trd] = 2 * trn_cost
        else:
            data['trn_cost'].iloc[trd] = 0

        final_trn_cost = data['trn_cost'].shift(1)
        print('Transaction cost:', final_trn_cost)
        
        # Lagging our trading signals by one period
        trading_positions_final = trading_positions.shift(1) * trading_qty

        # data['returns'] = np.log(data['Close'] / data['Close'].shift(1))
        data['returns']=(data['Close'].shift(1) / data['Close'])-1
        data['strat_returns'] = data['returns'] * trading_positions_final -  - final_trn_cost
        cum_returns = data['strat_returns'].dropna().cumsum()#.apply(np.exp)
        # print(data['strat_returns'].sum())
        print (cum_returns)

        # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))
        #
        # ax1.plot(data.loc[since:, :].index, data.loc[since:, 'Close'], label = 'Price')
        # # ax1.plot(ema_short.loc[since:, :].index, ema_short.loc[since:, 'Close'], label = "89 EMA")
        # ax1.legend(loc='best')
        # ax1.set_ylabel('Price($)')
        #
        # ax2.plot(cum_returns.loc[since:, :].index, cum_returns[since:, 'Close'],
        #          label='Equity Curve')
        # ax2.set_ylabel('Equity Curve')
        #
        # plt.show()

    return data['strat_returns'], cum_returns

returns, equity_curve = strategy(data)
print(returns, equity_curve)
# backtest.drawdown_periods(returns)
# backtest.underwater_plot(returns)









# import ccxt
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# # import pyfolio as pf
# import csv; import datetime; import pytz
# from technical_indicators import BBANDS
# from historical_data import exchange_data,write_to_csv,to_unix_time
# # import backtest
# import warnings
# warnings.filterwarnings('ignore')

# # ==========Initial trade parameters =============
# symbol = 'BTC/USD'
# timeframe = '5m'
# trading_qty = 1.0
# since = '2017-01-01 00:00:00'
# hist_start_date = int(to_unix_time(since))
# header = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
# period = []

# # ==========Initial exchange parameters =============
# kraken = exchange_data('kraken', 'BTC/USD', timeframe=timeframe, since=hist_start_date)
# write_to_csv(kraken,'BTC/USD','kraken')

# data = pd.DataFrame(kraken, columns=header)
# print(data.head())

# # ============ Strategy Function - Exponential Moving average crossover ================
# def strategy(data):
#     for period in range(20,100,5):
#         ema_short = data['Close'].ewm(span=period, adjust=False).mean()

#         # Difference between prices & EMA timeseries
#         trading_positions_raw = data['Close'] - ema_short
#         #trading_positions_raw.tail()

#         # Taking the sign of the difference to determine whether the price or EMA is greater and then
#         # multiply by qty

#         trading_positions = trading_positions_raw.apply(np.sign)
#         print('Trading Positions:', trading_positions.head())

#         # Lagging our trading signals by one period
#         trading_positions_final = trading_positions.shift(1) * trading_qty

#         data['returns'] = np.log(data['Close'].shift(1) / data['Close'])

#         data['strat_returns'] = data['returns'] * trading_positions_final
#         cum_returns = data['strat_returns'].dropna().cumsum().apply(np.exp)

#         print cum_returns

#         # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 9))
#         #
#         # ax1.plot(data.loc[since:, :].index, data.loc[since:, 'Close'], label = 'Price')
#         # # ax1.plot(ema_short.loc[since:, :].index, ema_short.loc[since:, 'Close'], label = "89 EMA")
#         # ax1.legend(loc='best')
#         # ax1.set_ylabel('Price($)')
#         #
#         # ax2.plot(cum_returns.loc[since:, :].index, cum_returns[since:, 'Close'],
#         #          label='Equity Curve')
#         # ax2.set_ylabel('Equity Curve')
#         #
#         # plt.show()

#     return data['strat_returns'], cum_returns

# returns, equity_curve = strategy(data)
# print(returns, equity_curve)
# # backtest.drawdown_periods(returns)
# # backtest.underwater_plot(returns)
