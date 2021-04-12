from datetime import time

# note data should be today only
import pandas as pd


def convert_data(df):
    times = [(time(9, 15), time(10, 15)), (time(10, 15), time(11, 15)), (time(11, 15), time(12, 15)),
             (time(12, 15), time(13, 15)), (time(14, 15), time(15, 15))]

    data = pd.DataFrame()
    for tup in times:
        try:
            dff = df[df.index.time < tup[1]]
            dff = dff[dff.index.time >= tup[0]]

            data = pd.concat([data, pd.DataFrame({
                'Time': [dff.index[0]],
                'Open': [dff['Open'][0]],
                'High': [dff['High'].max()],
                'Low': [dff['Low'].min()],
                'Close': [dff['Close'][-1]],
                'Volume': [dff['Volume'].sum()]
            })])
        except IndexError:
            break
    data.set_index('Time',inplace=True)
    return data


if __name__ == "__main__":
    print("Hello")
