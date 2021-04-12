import pandas as pd
from datetime import time
import os
import datetime as dt

cwd = r"F:\Database\Stock_Data\2018-2020"


def get_data(stock, time_period):
    stock_file = stock + ".csv"
    stock_file_loc = os.path.join(cwd, stock_file)
    data = pd.read_csv(stock_file_loc)
    data['Time'] = pd.to_datetime(data['Time'])
    data.set_index('Time', inplace=True)

    # resampling use : "1T","5T","D"
    # if time_period != '1T':
    #     conversion = {'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'}
    #     data = data.resample(time_period).agg(conversion)
    #     data.dropna(inplace=True)

    # setting Data between Market hours
    # note make changes if you want weekly or monthly data
    if time_period != "D" and time_period != "1H":
        data = data[data.index.time >= dt.datetime(2020, 2, 2, 9, 15).time()]
        data = data[data.index.time <= dt.datetime(2020, 2, 2, 15, 30).time()]
        data.dropna(inplace=True)
    return data


def add(data, b):
    # utility function
    # appends the value in dictionary 'b'
    # to corresponding key in dictionary 'data'
    for (key, value) in b.items():
        data[key].append(value)


def get_hourly_data(symbol):
    df = get_data(symbol, '1min')
    df.reset_index(inplace=True)
    # stores hourly data to convert to dataframe
    data = {
        'Time': [],
        'Open': [],
        'High': [],
        'Low': [],
        'Close': [],
        'Volume': []
    }

    start_time = [time(9, 16), time(10, 15), time(11, 15), time(
        12, 15), time(13, 15), time(14, 15), time(15, 15)]

    end_time = [time(10, 14), time(11, 14), time(12, 14), time(
        13, 14), time(14, 14), time(15, 14), time(15, 29)]

    # Market timings 9:15am to 3:30pm (6 hours 15 mins)
    # We create 6 hourly bars and one 15 min bar
    # as usually depicted in candlestick charts
    i = 0
    no_bars = df.shape[0]
    start_idx = 0
    while i < no_bars:

        if df.loc[i, 'Time'].time() in end_time:
            end_idx = i + 1

            hour_df = df[start_idx:end_idx]

            add(data, {
                'Time': df.loc[start_idx]['Time'],
                'Open': hour_df['Open'].iloc[0],
                'High': hour_df['High'].max(),
                'Low': hour_df['Low'].min(),
                'Close': hour_df['Close'].iloc[-1],
                'Volume': hour_df['Volume'].sum()
            })

        if df.loc[i, 'Time'].time() in start_time:
            start_idx = i

            # optional optimisation for large datasets
            # skip ahead to loop faster
            # i += 55

        i += 1

    df = pd.DataFrame(data=data).set_index(keys=['Time'])
    # df.to_csv('out.csv')
    df.reset_index(inplace=True)
    for e in df.index:
        if df.loc[e, 'Time'].time() == time(9, 16):
            df.loc[e, 'Time'] = dt.datetime.combine(df.loc[e, 'Time'].date(), time(9, 15))
    df.set_index('Time', drop=True, inplace=True)
    return df


if __name__ == "__main__":
    df = get_hourly_data('SBIN')
