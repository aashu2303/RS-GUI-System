from settings import *
import sqlite3
import os
import datetime
import pandas as pd

nse_holidays = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute("SELECT * FROM nse_holidays")))
symbols = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute(symbols_query)))
columns = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute(columns_query)))
indices = list(map(lambda x: x[0], sqlite3.connect(dbpath).cursor().execute(indices_query)))

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
    while count > 0:
        if isHoliday(date):
            date -= datetime.timedelta(days=1)
        else:
            date -= datetime.timedelta(days=1)
            count -= 1
    return date

def lastndaysweekly(date, freq, day):
    count = 1
    while count < freq:
        if date.strftime("%A") == day:
            count += 1
            date -= datetime.timedelta(days=7)
        else:
            date -= datetime.timedelta(days=1)
    return previousTradingDay(date)

def lastndaysmonthly(date, freq):
    dates = []
    count = freq
    while count > 0:
        if pd.to_datetime(date).is_month_end:
            dates.append(previousTradingDay(date))
            date -= datetime.timedelta(days=date.day)
            count -= 1
        else:
            date -= datetime.timedelta(days=1)
    dates.append(previousTradingDay(date))
    return dates

def previousmonthEnd(date):
    date -= datetime.timedelta(days=1)
    while not pd.to_datetime(date).is_month_end:
        date -= datetime.timedelta(days=1)
    else:
        return date

def previousquarterEnd(date):
    date = previousmonthEnd(date)
    while not pd.to_datetime(date).is_quarter_end:
        date = previousmonthEnd(date)
    return date

def lastndaysquarterly(date, freq):
    dates = []
    count = freq
    while count > 0:
        if pd.to_datetime(date).is_quarter_end:
            dates.append(previousTradingDay(date))
            count -= 1
        date -= datetime.timedelta(days=date.day)
    dates.append(previousTradingDay(date))
    return dates

def nextndaysdaily(date, freq):
    count = freq+1
    while count > 0:
        if isHoliday(date):
            date += datetime.timedelta(days=1)
        else:
            date += datetime.timedelta(days=1)
            count -= 1
    return nextTradingDay(date)

def nextndaysweekly(date, freq):
    count = freq
    while count > 0:
        date += datetime.timedelta(days=7)
        count -= 1
    return previousTradingDay(date)

def nextMonthend(date):
    date += datetime.timedelta(days=1)
    while not pd.to_datetime(date).is_month_end:
        date += datetime.timedelta(days=1)
    return date

def nextQuarterend(date):
    date = nextMonthend(date)
    while not pd.to_datetime(date).is_quarter_end:
        date = nextMonthend(date)
    return date
def nextndaysmonthly(date, freq):
    dates = []
    count = freq + 1
    date = nextMonthend(date)
    while count > 0:
        dates.append(previousTradingDay(nextMonthend(date)))
        date = nextMonthend(date)
        count -= 1
    # return dates, date
    return date

def nextndaysquarterly(date, freq):
    dates = []
    count = freq + 1
    date = nextQuarterend(date)
    while count > 0:
        dates.append(previousTradingDay(nextQuarterend(date)))
        date = nextQuarterend(date)
        count -= 1
    return date

def previousTradingDay(date):
    while isHoliday(date):
        date -= datetime.timedelta(days=1)
    else:
        return date

def nextTradingDay(date):
    while isHoliday(date):
        date += datetime.timedelta(days=1)
    else:
        return date

def updateDb(dbpath):
    dbconn = sqlite3.connect(dbpath)
    lastday = lastTradingDay(dbpath)
    while lastday < previousTradingDay(datetime.datetime.today().date()):
        lastday += datetime.timedelta(days=1)
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
            return True

if __name__ == '__main__':
    date = previousmonthEnd(datetime.datetime.today().date())
    print(date)
    print(previousmonthEnd(date))
    print(previousquarterEnd(date))