import pandas as pd
import numpy as np
from util import alpaca_util as alpaca


# Benchmark (HODLer strat)
def benchmark(df_prices, symbol, share_max=1):
    df_trades = df_prices.copy()
    df_trades[:] = 0

    data = np.zeros(df_trades.shape[0])
    data[0] = share_max # TODO change this to max @ cash avail + fractional?

    df_trades.insert(0, symbol, data, True)

    return df_trades


def compute_portvals(df_orders=pd.DataFrame([]), start_val=1000000, commission=9.95, impact=0.005, df_prices = pd.DataFrame([])):
    df_orders.sort_index(inplace=True)
    symbols = list(df_orders)
    start_date = df_orders.index[0]
    end_date = df_orders.index[-1]

    symbol = symbols[0]

#    adj_close = alpaca.get_prices(symbol, start_date, end_date)['close']
#    df_prices = pd.DataFrame({symbol: adj_close})

    df_prices.fillna(method='ffill', inplace=True)
    df_prices.fillna(method='backfill', inplace=True)

    df_prices["CASH"] = 1

    df_trades = df_prices.copy()
    df_trades[:] = 0.0
    df_holdings = df_trades.copy()

    # Sleepy 3/28 AM edits, but start date might not be allowed...
    start_date = df_holdings.index[0]

    df_holdings.at[start_date, 'CASH'] = start_val

    # !! trades has short format index
    # !! orders has long format index
    for index, row in df_orders.iterrows():
        order = row.iloc[0]
        symbol = symbols[0]

        if (index in df_trades.index):
            currShare = df_trades.at[index, symbol]
            currCASH = df_trades.at[index, "CASH"]
            price = df_prices.at[index, symbol]
            # Mad restructure opportunity with new input organization. This could all be one block /I think/
            if (order < 0):
                price = price * (1 - impact)
                df_trades.at[index, symbol] = currShare - (-1 * order)
                df_trades.at[index, "CASH"] = currCASH + (price * (-1 * order)) - commission
            if (order > 0):
                price = price * (1 + impact)
                df_trades.at[index, symbol] = currShare + order
                df_trades.at[index, "CASH"] = currCASH - (price * order) - commission

    df_holdings = df_trades.cumsum()
    df_holdings["CASH"] = df_holdings["CASH"] + start_val

    df_value = df_holdings * df_prices

    df_port_val = df_value.sum(axis=1)

    rv = pd.DataFrame(index=df_port_val.index, data=df_port_val.values)
    rv = clean_up(rv)
    return rv


# 3/28 I have no idea what this was for
def clean_up(portvals):
    if isinstance(portvals, pd.DataFrame):
        return portvals[portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"


# 3/28 still needs review as well
def port_stats(portvals, title, verbose=True):
    # Get portfolio stats
    daily_returns = portvals.copy()
    daily_returns[1:] = (portvals[1:] / portvals[:-1].values) - 1
    daily_returns = daily_returns[1:]
    cum_ret = (portvals[-1] / portvals[0]) - 1
    average_daily_ret = daily_returns.mean()
    std_daily_ret = daily_returns.std()
    sr = average_daily_ret / std_daily_ret  # ignoring rf since it is 0.0 anyways
    sr_daily = 252 ** 0.5 * sr

    if (verbose):
        print("")
        print(title, ":")
        # Compare portfolio against $SPX
        #	print "Date Range: {} to {}".format(start_date, end_date)
        print("Sharpe Ratio of Fund: {}".format(sr_daily))
        #	print "Sharpe Ratio of SPY : {}".format(sharpe_ratio_SPY)
        print("Cumulative Return of Fund: {}".format(cum_ret))
        #	print "Cumulative Return of SPY : {}".format(cum_ret_SPY)
        print("Standard Deviation of Fund: {}".format(std_daily_ret))
        #	print "Standard Deviation of SPY : {}".format(std_daily_ret_SPY)
        print("Average Daily Return of Fund: {}".format(average_daily_ret))
        #	print "Average Daily Return of SPY : {}".format(avg_daily_ret_SPY)
        print("Final Portfolio Value: {}".format(portvals[-1]))

    out = {
        "sr": sr_daily,
        "cum_ret": cum_ret,
        "std_daily_ret": std_daily_ret,
        "average_daily_ret": average_daily_ret,
        "final_value": portvals[-1]
    }
    return out
