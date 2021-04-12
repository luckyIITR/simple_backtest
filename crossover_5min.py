from portfolio_file_gen import Portfolio
import os
import pandas as pd
import datetime as dt
import mplfinance as mpf
from finta import TA
from hour_data import get_hourly_data
from datetime import time
from hourly_converter import convert_data
from datetime import timedelta

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
    if time_period != "D" and time_period != "1H":
        data = data[data.index.time >= dt.datetime(2020, 2, 2, 9, 15).time()]
        data = data[data.index.time <= dt.datetime(2020, 2, 2, 15, 15).time()]
        data.dropna(inplace=True)
    return data


def plot_data(data):
    mpf.plot(data, type='candle', volume=True, style='yahoo', tight_layout=True)


symbol = "SBIN"
Hour_df = get_hourly_data(symbol)
# plot_data(df_5min[:70])
rsi = TA.RSI(Hour_df).shift(1)
Hour_df['Pre_RSI'] = rsi
# Hour_df = Hour_df[49:]

Hour_df = Hour_df.loc[~Hour_df.index.duplicated(keep='first')]
df_5min = get_data(symbol, '5min')
df_5min = df_5min[df_5min.index >= Hour_df.index[0]]
df_5min = pd.concat([df_5min, Hour_df['Pre_RSI']], axis=1)
df_5min.ffill(inplace=True)
df_5min['2DEMA'] = TA.EMA(df_5min, 2)
df_5min['10DEMA'] = TA.EMA(df_5min, 10)
df_5min['ATR'] = TA.ATR(df_5min)
df_5min = df_5min[511:]
RSI = []

start_time = [time(9, 15), time(10, 15), time(11, 15), time(
    12, 15), time(13, 15), time(14, 15), time(15, 15)]
# i = 0
# e = df_5min.index[13]
for e in df_5min.index:
    # break
    if e.time() in start_time:
        hour_temp = Hour_df[Hour_df.index < e]
    else:
        hour_temp = Hour_df[Hour_df.index < e]
        hour_temp = hour_temp[:-1]
    df5min_temp = df_5min[df_5min.index.date == e.date()]
    df5min_temp = df5min_temp[df5min_temp.index.time <= e.time()]
    today_hourly = convert_data(df5min_temp)
    # df = df5min_temp
    hour_temp = pd.concat([hour_temp, today_hourly.iloc[[-1]]], axis=0)
    RSI.append(TA.RSI(hour_temp).values[-1])
    # if e.time() == time(10,10):
    #     break
    # i = i+1

rsi2 = RSI
# RSI = rsi2
# df_5min.to_csv('RSI_data_sbi.csv')
df_5min['RSI'] = RSI
#
# dfff = pd.read_csv('RSI_data_sbi.csv')
# RSI = dfff['RSI'].values

port = Portfolio(symbol)
i = 0
for e in df_5min.index:
    if e.time() == time(9, 15):
        continue
    buy_condition = False
    buy_condition = df_5min.loc[e, '2DEMA'] > df_5min.loc[e, '10DEMA'] and df_5min.loc[
        e - timedelta(minutes=5), '2DEMA'] < \
                    df_5min.loc[e - timedelta(minutes=5), '10DEMA'] and df_5min.loc[e, 'Pre_RSI'] < 40 and df_5min.loc[
                        e, 'RSI'] > df_5min.loc[e, 'Pre_RSI'] and e.time() < time(15, 15)

    if buy_condition and port.status == 0:
        bp = df_5min.loc[e, 'Close']
        tgt1 = bp + df_5min.loc[e, 'ATR'] * 2
        tgt2 = bp + df_5min.loc[e, 'ATR'] * 3
        sl = bp - df_5min.loc[e, 'ATR'] * 2
        qty = int(500 / (bp - sl))
        port.buy(df_5min.loc[e, 'Close'], e, qty)
        port.status = 1
        port.partial_status = 0
        continue
    if port.status == 1:
        if df_5min.loc[e, 'High'] > tgt1 and port.partial_status == 0 and e.time() < dt.datetime(2020, 2,
                                                                                                 2, 15,
                                                                                                 15).time():
            port.book_partial(tgt1, e, qty)
            port.partial_status = 1
        elif df_5min.loc[e, 'High'] > tgt2 and e.time() < dt.datetime(2020, 2,
                                                                      2, 15,
                                                                      15).time():
            port.target(tgt2, e, qty)
            port.status = 0
        elif df_5min.loc[e, 'Low'] < sl and e.time() < dt.datetime(2020, 2,
                                                                   2, 15,
                                                                   15).time():
            port.sl(sl, e, qty)
            port.status = 0
        if port.status == 1 and e.time() == dt.datetime(2020, 2, 2, 15, 15).time():
            port.forced_closed(df_5min.loc[e, 'Open'], e, qty)
            port.status = 0
port.save_data()
