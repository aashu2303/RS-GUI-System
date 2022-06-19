import sqlite3
import datetime

dbconn = sqlite3.connect("stockdata.db")
cursor = dbconn.cursor()

symbol_list = cursor.execute("SELECT distinct symbol FROM stocks order by symbol").fetchall()
symbol_list = list(map(lambda x: x[0], symbol_list))
holidays_list = list(map(lambda x: x[0],
                         cursor.execute("SELECT distinct date FROM nse_holidays order by date desc").fetchall()))
# print(symbol_list)
# print(len(symbol_list))
# print(holidays_list)
ls = []
for sym in symbol_list:
    data = cursor.execute("SELECT date from stocks where symbol=:sym order by date", {"sym": sym}).fetchall()
    data = list(map(lambda x: datetime.datetime.strptime(x[0], "%Y/%m/%d").date(), data))

    startdate = min(data)
    enddate = max(data)

    # print(f"Start : {startdate}")
    # print(f"End : {enddate})
    if sym != "NSENIFTY":
        continue
    print(sym)
    while startdate <= enddate:
        if startdate.strftime("%Y-%m-%d") not in holidays_list:
            if startdate.strftime("%A") != "Saturday" and startdate.strftime("%A") != "Sunday":
                if startdate not in data and startdate.strftime("%Y-%m-%d") not in ls:
                    ls.append(startdate.strftime("%Y-%m-%d"))

        # if startdate not in data:
        #     if startdate.strftime("%Y-%m-%d") not in ls:
        #         ls.append(startdate.strftime("%Y-%m-%d"))

        startdate += datetime.timedelta(days=1)
    # print(ls)
assert len(ls) == len(set(ls))
ls.sort(key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
print(ls)
