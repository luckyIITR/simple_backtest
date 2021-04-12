import pandas as pd


class Portfolio:

    def __init__(self, symbol):
        self.symbol = symbol
        self.status = 0
        self.order_book = pd.DataFrame()
        self.partial_status = 0

    def buy(self, bp, time, qty):
        self.order_book = pd.concat([self.order_book, pd.DataFrame({'Price': [bp], 'Status': ['BUY'], 'Time': [time], "Qty" : [qty]})],
                                    axis=0)

    def book_partial(self, sp, time, qty):
        self.order_book = pd.concat(
            [self.order_book, pd.DataFrame({'Price': [sp], 'Status': ['PartialBooked'], 'Time': [time], "Qty" : [qty]})], axis=0)

    def target(self, sp, time, qty):
        self.order_book = pd.concat(
            [self.order_book, pd.DataFrame({'Price': [sp], 'Status': ['Target'], 'Time': [time], "Qty" : [qty]})], axis=0)

    def sl(self,sp, time, qty):
        self.order_book = pd.concat([self.order_book, pd.DataFrame({'Price': [sp], 'Status': ['SL'], 'Time': [time], "Qty" : [qty]})], axis=0)

    def forced_closed(self, sp, time, qty):
        self.order_book = pd.concat(
            [self.order_book, pd.DataFrame({'Price': [sp], 'Status': ['Forced_closed'], 'Time': [time], "Qty" : [qty]})], axis=0)

    def save_data(self):
        self.order_book.to_csv("C:/Users/lucky/PycharmProjects/simple_backtest/Result/" + self.symbol + ".csv")
