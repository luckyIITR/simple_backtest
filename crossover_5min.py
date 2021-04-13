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
import yfinance as yf
import talib


def plot_data(data):
    mpf.plot(data, type='candle', volume=True, style='yahoo', tight_layout=True)


symbol = "INDUSINDBK"
Hour_df = yf.download(symbol + '.NS', interval='60m', start="2021-01-14", end='2021-04-12')
Hour_df.index = Hour_df.index.tz_localize(None)
# plot_data(Hour_df)
rsi = talib.RSI(Hour_df['Close'], timeperiod=14)
Hour_df['Pre_RSI'] = rsi.shift(1)
# Hour_df = Hour_df[49:]

Hour_df = Hour_df.loc[~Hour_df.index.duplicated(keep='first')]
df_5min = yf.download(symbol + '.NS', interval='5m', period="60d")
df_5min = df_5min[df_5min.index.date < dt.datetime(2021, 4, 13, 0, 0).date()]
df_5min.index = df_5min.index.tz_localize(None)
df_5min = df_5min[df_5min.index >= Hour_df.index[0]]
df_5min = df_5min[df_5min.index <= Hour_df.index[-1]]

df_5min = pd.concat([df_5min, Hour_df['Pre_RSI']], axis=1)
df_5min.ffill(inplace=True)
df_5min['2DEMA'] = talib.EMA(df_5min['Close'], 2)
df_5min['10DEMA'] = talib.EMA(df_5min['Close'], 10)
df_5min['ATR'] = talib.ATR(df_5min['High'], df_5min['Low'], df_5min['Close'], timeperiod=14)
df_5min = df_5min[225:]
RSI = []

start_time = [time(9, 15), time(10, 15), time(11, 15), time(
    12, 15), time(13, 15), time(14, 15), time(15, 15)]
# i = 0
e = df_5min.index[48]
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
    RSI.append(talib.RSI(hour_temp['Close'], timeperiod=14).values[-1])
    # if e.time() == time(12, 50):
    #     break
    # i = i + 1

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
                    df_5min.loc[e - timedelta(minutes=5), '10DEMA'] and 60 < df_5min.loc[e, 'Pre_RSI'] < df_5min.loc[
                        e, 'RSI'] and e.time() < time(15, 15)

    if buy_condition and port.status == 0:
        bp = df_5min.loc[e, 'Close']
        tgt1 = bp + df_5min.loc[e, 'ATR'] * 2
        tgt2 = bp + df_5min.loc[e, 'ATR'] * 4
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

# df_5min['RSI'].plot()
