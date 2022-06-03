import datetime
import sqlite3
import pandas as pd
from settings import *
from utils import previousTradingDay

def get_monthly_closes():
    ls = []
    date = datetime.datetime.today().date()
    while date.year >= 1994:
        if pd.to_datetime([date]).is_month_end:
            ls.append(previousTradingDay(date).strftime("%Y/%m/%d"))
        date -= datetime.timedelta(days=1)
    return ls

closes = get_monthly_closes()

data = sqlite3.connect(dbpath).cursor().execute(f"SELECT date FROM stocks where date in {tuple(closes)} and symbol='RELIANCE' order by date").fetchall()
data = list(map(lambda x: x[0], data))

print(set(closes) - set(data))