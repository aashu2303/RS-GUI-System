import sqlite3
import pandas as pd
from utils import dbpath, nse_holidays, symbols
import os
from sqlite3 import IntegrityError

columns = ['symbol','date','open', 'high', 'low', 'close', 'volume', 'OI']
# data = pd.read_csv("Full_Data/data.txt", delimiter=",", names=columns)[["symbol", 'date', 'close']]


dbconn = sqlite3.connect(dbpath)
cur = dbconn.cursor()
# cur.execute(""" CREATE TABLE IF NOT EXISTS stocks(
#     symbol TEXT NOT NULL,
#     date TEXT NOT NULL,
#     close NUMERIC NOT NULL,
#     PRIMARY KEY (symbol, date)
# ) """)

# try:
#     data.to_sql(name='stocks', con=dbconn, if_exists="append", index=False)
# except IntegrityError as e:
#     print(f"{e} Encountered. Insertion stopped")
# cur.execute("""
#     INSERT INTO stocks(symbol, date, close)
#     VALUES (:symbol, :date, :close)
# """, {"symbol": data.loc[0, 'symbol'], "date": data.loc[0, 'date'], "close": data.loc[0, 'close']})

# symbol_list = pd.read_csv("Full_Data/ind_nifty500list.csv", delimiter=",", names=['name', "industry", 'symbol', 'series', 'ISIN'], header=None)[1:]['symbol'].to_list()
#
# addn_list = ['NSENIFTY', "NSE100", "NSE500", "NSEMIDCAP", "NIFTYAUTO", "BANKNIFTY", "NIFTYFINSERVICE", "NIFTYFMGC", "NSEIT", "NIFTYMEDIA", "NIFTYMETAL", "NIFTYPHARMA", "NIFTYPVTBANK", "NIFTYPSUBANK", "NIFTYREALTY", "NIFTYCOMMODITIES", "NIFTYCONSUMPTION", "NIFTYCPSE", "NIFTYENERGY", "NIFTY100ESG", "NIFTY100ENHESG", "NIFTYINFRA", "NIFTYMNC", "NIFTYPSE", "VIX"]
# for sym in addn_list:
#     symbol_list.append(sym)
# # print(pd.Series(symbol_list))
# # pd.Series(symbol_list, name="symbol").to_sql(name="symbol_list", con=dbconn, if_exists="append", index=False)
#
# data = data[data['symbol'].isin(symbol_list)]
# print(len(symbol_list))
# try:
#     data.to_sql(name="stocks", con=dbconn, index=False, if_exists="append")
# except IntegrityError as e:
#     print(f"{e} Encountered. Insertion halted")
#
# hols = pd.Series(nse_holidays, name="date")
# try:
#     hols.to_sql(name="nse_holidays", con=dbconn, if_exists="append", index=False)
# except IntegrityError as e:
#     print(f"{e} Encountered. Cannot proceed")
# # assert len(data['symbol'].unique()) == len(symbol_list)

def daily_append():
    data = pd.read_csv("Full_Data/eq1.csv", names=columns)[['symbol', 'date', 'close']]
    data['date'] = data['date'].apply(lambda x: f"{str(x)[:4]}/{str(x)[4:6]}/{str(x)[6:]}")
    cols = data.columns
    data = data[data['symbol'].isin(symbols)].reset_index(drop=True)
    print(data)
    print(len(data))

    data.to_sql(name='stocks', con=dbconn, if_exists="append", index=False)
    print("Done")


if __name__ == '__main__':
    daily_append()
