import datetime
from datetime import timedelta
import os
import sqlite3
import pandas as pd
from sql_queries import *

LOGIN = str(7032655929)
PASSWORD = "Aaseesh@4143"
dbpath = os.path.join(os.getcwd(), "stockdata.db")
nse_holidays = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute("SELECT * FROM nse_holidays")))
symbols = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute(symbols_query)))
columns = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute(columns_query)))
cwd = os.getcwd()
report_dir_path = os.path.join(cwd, 'Batch Reports')
datapath = r"C:\BHAVCOPY\EQ"
bhavfilename = r"-NSE-EQ.txt"

def isHoliday(date):
    name = date.strftime("%A")
    if date.strftime("%Y-%m-%d") in nse_holidays or name == "Sunday" or name == "Saturday":
        return True
    return False

def lastTradingDay(path):
    db_conn = sqlite3.connect(path)
    cur = db_conn.cursor()
    data = list(map(lambda x: x[0], cur.execute(times_query)))
    data = list(map(lambda x: datetime.datetime.strptime(x, "%Y/%m/%d").date(), data))
    return max(data)

def lastndaysdaily(date, freq):
    count = freq
    while(count > 0):
        if isHoliday(date):
            date -= timedelta(days=1)
        else:
            date -= timedelta(days=1)
            count -= 1
    return date

def lastndaysweekly(date, freq):
    count = freq
    while(count > 0):
        if isHoliday(date):
            date -= timedelta(days=1)
        else:
            date -= timedelta(days=7)
            count -= 1
    return date


def previousTradingDay(date):
    while(isHoliday(date)):
        date -= timedelta(days=1)
    else:
        return date

def updateDb(dbpath):
    dbconn = sqlite3.connect(dbpath)
    lastday = lastTradingDay(dbpath)
    while lastday < previousTradingDay(datetime.datetime.today().date()):
        lastday += timedelta(days=1)
        print(lastday)
        if lastday.strftime("%Y-%m-%d") not in nse_holidays:
            filepath = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + bhavfilename)
            csvfile = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + ".csv")

            try:
                os.rename(filepath, csvfile)
            except FileNotFoundError:
                print(f"File {filepath} not found")
                return False

            data = pd.read_csv(csvfile, delimiter=",", names=["symbol", "date", "open", "high", "low", "close", "volume", "openI"])[["symbol", "date", "close"]]
            data['date'] = data['date'].apply(lambda x: f"{str(x)[:4]}/{str(x)[4:6]}/{str(x)[6:8]}")
            data = data[data['symbol'].isin(symbols)]
            try:
                data.to_sql(name="stocks", con=dbconn, if_exists="append", index=False)
            except sqlite3.IntegrityError as e:
                print(f"{e} occured")

    return False
if __name__ == '__main__':
    updateDb(dbpath)
