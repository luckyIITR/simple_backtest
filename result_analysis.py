import pandas as pd
import os
import matplotlib.pyplot as plt

# plt.ioff()

cwd = r"C:\Users\lucky\PycharmProjects\simple_backtest\Result"
files = os.listdir(cwd)

main_data = pd.DataFrame()
# capital = 10000
# files = files[:-1]
for file in files:
    # break
    flag = 0
    # plt.figure(figsize=(14, 7))
    df = pd.read_csv(os.path.join(cwd, file))
    df.set_index('Time', inplace=True)
    bp = 0
    sl = 0
    pb = 0
    tgt1 = 0
    tgt2 = 0
    fc = 0
    trade_book = pd.DataFrame()
    for e in df.index:
        if df.loc[e, 'Status'] == "BUY":
            bp = df.loc[e, 'Price']
            qty = df.loc[e, "Qty"]
        elif df.loc[e, 'Status'] == "PartialBooked":
            tgt1 = df.loc[e, 'Price']
        elif df.loc[e, 'Status'] == "Target":
            tgt2 = df.loc[e, "Price"]
        elif df.loc[e, 'Status'] == "SL":
            sl = df.loc[e, 'Price']
        elif df.loc[e, "Status"] == 'Forced_closed':
            fc = df.loc[e, 'Price']

        if tgt2 != 0 or sl != 0 or fc != 0:
            trade_book = pd.concat([trade_book, pd.DataFrame(
                {"Time": [e], 'BP': [bp], 'SL': [sl], 'TGT1': [tgt1], 'TGT2': [tgt2], 'FC': [fc], 'Qty': [qty]})])
            bp = 0
            sl = 0
            pb = 0
            tgt1 = 0
            tgt2 = 0
            fc = 0

    trade_book.set_index('Time', inplace=True, drop=True)
    profit = []
    for e in trade_book.index:
        if trade_book.loc[e, 'TGT2'] != 0:
            profit.append((trade_book.loc[e, 'TGT1'] - trade_book.loc[e, 'BP']) * trade_book.loc[e, 'Qty'] / 2 + (
                    trade_book.loc[e, 'TGT2'] - trade_book.loc[e, 'BP']) * (
                                  trade_book.loc[e, 'Qty'] - trade_book.loc[e, 'Qty'] / 2))
        if trade_book.loc[e, 'SL'] != 0:
            if trade_book.loc[e, 'TGT1'] != 0:
                profit.append(
                    (trade_book.loc[e, 'TGT1'] - trade_book.loc[e, 'BP']) * trade_book.loc[e, 'Qty'] / 2 + (
                            trade_book.loc[e, 'SL'] - trade_book.loc[e, 'BP']) * (
                            trade_book.loc[e, 'Qty'] - trade_book.loc[e, 'Qty'] / 2))
            else:
                profit.append((trade_book.loc[e, 'SL'] - trade_book.loc[e, 'BP']) * trade_book.loc[e, "Qty"])
        if trade_book.loc[e, 'FC'] != 0:
            if trade_book.loc[e, 'TGT1'] != 0:
                profit.append(
                    (trade_book.loc[e, 'TGT1'] - trade_book.loc[e, 'BP']) * trade_book.loc[e, 'Qty'] / 2 + (
                            trade_book.loc[e, 'FC'] - trade_book.loc[e, 'BP']) * (
                            trade_book.loc[e, 'Qty'] - trade_book.loc[e, 'Qty'] / 2))
            else:
                profit.append((trade_book.loc[e, 'FC'] - trade_book.loc[e, 'BP']) * trade_book.loc[e, "Qty"])
    trade_book['P_L'] = profit
    trade_book['Cumsum'] = trade_book['P_L'].cumsum()
    plt.plot(trade_book['Cumsum'])
