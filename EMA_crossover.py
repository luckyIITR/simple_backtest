from portfolio_file_gen import Portfolio
import os
import pandas as pd
import datetime as dt
import mplfinance as mpf
from finta import TA
from datetime import timedelta
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

cwd = r"F:\Database\Stock_Data\2018-2020"


def get_data(stock, time_period):
    stock_file = stock + ".csv"
    stock_file_loc = os.path.join(cwd, stock_file)
    data = pd.read_csv(stock_file_loc)
    data['Time'] = pd.to_datetime(data['Time'])
    data.set_index('Time', inplace=True)

    # resampling use : "1T","5T","D"
    if time_period != '1T':
        conversion = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
        data = data.resample(time_period).agg(conversion)
        data.dropna(inplace=True)

    # setting Data between Market hours
    # note make changes if you want weekly or monthly data
    if time_period != "D":
        data = data[data.index.time >= dt.datetime(2020, 2, 2, 9, 15).time()]
        data = data[data.index.time <= dt.datetime(2020, 2, 2, 15, 15).time()]
        data.dropna(inplace=True)
    return data


# check end data points only for intra day data
def check_data(data):
    dates = sorted(list(set(data.index.date)))
    # date = dates[0]
    for date in dates:
        if data[data.index.date == date].index[0].time() != dt.datetime(2020, 2, 2, 9, 15).time() and \
                data[data.index.date == date].index[-1].time() != dt.datetime(2020, 2, 2, 15, 15).time():
            print(f"There is Fault in data at date : {date}")


def plot_data(data):
    mpf.plot(data, type='candle', volume=True, style='yahoo', tight_layout=True)


symbols = ['CIPLA', 'SUNPHARMA', 'HINDUNILVR', 'TECHM',
           'TATACONSUM', 'WIPRO', 'DRREDDY', 'TITAN', 'JSWSTEEL',
           'TATAMOTORS', 'DIVISLAB', 'KOTAKBANK', 'HCLTECH', 'HDFC', 'ONGC',
           'SBILIFE', 'BHARTIARTL', 'TCS', 'MARUTI', 'BAJAJ-AUTO', 'INFY',
           'SHREECEM', 'ITC', 'POWERGRID', 'BAJAJFINSV', 'ADANIPORTS',
           'NESTLEIND', 'HEROMOTOCO', 'BRITANNIA', 'M&M', 'ASIANPAINT',
           'HDFCBANK', 'GRASIM', 'HDFCLIFE', 'SBIN', 'LT', 'INDUSINDBK',
           'BPCL', 'RELIANCE', 'IOC', 'EICHERMOT', 'COALINDIA', 'HINDALCO',
           'ICICIBANK', 'AXISBANK', 'NTPC', 'ULTRACEMCO', 'TATASTEEL', 'UPL',
           'BAJFINANCE']
# fetching data and cleaning
# symbols = ["INDUSINDBK"]
for symbol in symbols:
    try:
        # daily Data for RSI
        daily_df = get_data(symbol, 'D')
        rsi = TA.RSI(daily_df)
        daily_df['RSI'] = rsi.shift(1)
        daily_df = daily_df[30:]
        # plot_data(df)

        # 5 min data
        df_5min = get_data(symbol, '5T')
        df_5min["2DEMA"] = TA.EMA(df_5min, 2)
        df_5min["10DEMA"] = TA.EMA(df_5min, 10)
        df_5min['ATR'] = TA.ATR(df_5min)
        df_5min = df_5min[df_5min.index >= daily_df.index[0]]
        df_5min = pd.concat([df_5min, daily_df['RSI']], axis=1)
        df_5min.ffill(inplace=True)
        df_5min = df_5min[df_5min.index.time >= dt.datetime(2020, 2, 2, 9, 15).time()]
        df_5min = df_5min[df_5min.index.time <= dt.datetime(2020, 2, 2, 15, 15).time()]
        df_5min.dropna(inplace=True)

        df_5min['Signal'] = 0.0
        df_5min['Signal'] = [
            1 if df_5min.loc[e, '2DEMA'] > df_5min.loc[e, '10DEMA'] and df_5min.loc[e, 'RSI'] < 30 else 0 for e in
            df_5min.index]
        # df_5min['Signal'] = np.where(df_5min['2DEMA'] > df_5min['10DEMA'] and df_5min['RSI'] < 30, 1.0, 0.0)
        df_5min['Position'] = df_5min['Signal'].diff()

        dates = sorted(list(set(daily_df.index)))

        # object created
        port = Portfolio(symbol)

        # main Backtest
        for date in dates:
            # break
            today = df_5min[df_5min.index.date == date].copy()
            port.status = 0
            if today[today['Position'] == 1].empty:
                continue
            else:
                for e in today.index:
                    if e == today.index[0]:
                        continue
                    if today.loc[e, "Position"] == 1 and port.status == 0 and e.time() != dt.datetime(2020, 2, 2, 15,
                                                                                                      15).time():
                        port.status = 1
                        sl = today.loc[e, "Close"] - today.loc[e, 'ATR'] * 5
                        tgt1 = today.loc[e, "Close"] + today.loc[e, 'ATR'] * 5
                        tgt2 = today.loc[e, "Close"] + today.loc[e, 'ATR'] * 7
                        bp = today.loc[e, 'Close']
                        qty = int(500 / (bp - sl))
                        port.buy(today.loc[e, 'Close'], e, qty)
                        port.partial_status = 0
                        continue

                    if port.status == 1:
                        if today.loc[e, 'Low'] < sl and e.time() < dt.datetime(2020, 2,
                                                                               2, 15,
                                                                               15).time():
                            port.sl(sl, e, qty)
                            port.status = 0
                            continue
                    if port.status == 1:
                        if today.loc[e, 'High'] > tgt1 and port.partial_status == 0 and e.time() < dt.datetime(2020, 2,
                                                                                                               2, 15,
                                                                                                               15).time():
                            port.book_partial(tgt1, e, qty)
                            port.partial_status = 1
                            continue
                        if today.loc[e, 'High'] > tgt2 and e.time() < dt.datetime(2020, 2,
                                                                                  2, 15,
                                                                                  15).time():
                            port.target(tgt2, e, qty)
                            port.status = 0
                            continue
                    if port.status == 1 and e.time() == dt.datetime(2020, 2, 2, 15, 15).time():
                        port.forced_closed(today.loc[e, 'Open'], e, qty)
                        port.status = 0

        port.save_data()
    except FileNotFoundError:
        continue
