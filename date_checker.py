import sqlite3
import datetime

dbconn = sqlite3.connect("stockdata.db")
cursor = dbconn.cursor()

symbol_list = cursor.execute("SELECT distinct symbol FROM stocks order by symbol").fetchall()
symbol_list = list(map(lambda x: x[0], symbol_list))
holidays_list = list(map(lambda x: datetime.datetime.strptime(x[0], "%Y-%m-%d"), cursor.execute("SELECT distinct date FROM nse_holidays").fetchall()))
# print(symbol_list)
# print(len(symbol_list))
print(holidays_list)


for sym in symbol_list:
    data = cursor.execute("SELECT date from stocks where symbol=:sym order by date", {"sym": sym}).fetchall()
    data = list(map(lambda x: datetime.datetime.strptime(x[0], "%Y/%m/%d"), data))
    startdate = data[0]
    enddate = data[-1]
    ls = []
    while startdate <= enddate:
        if not (startdate in holidays_list or startdate.strftime("%A") == "Saturday" or startdate.strftime("%A") == "Sunday"):
            if startdate not in data:
                ls.append(startdate.strftime("%Y-%m-%d"))
        startdate += datetime.timedelta(days=1)
    print(sym, ls)

    # print(sym, data)