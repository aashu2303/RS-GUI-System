import pandas as pd
from utils import nse_holidays
from datetime import datetime, timedelta
import sqlite3

# # input_date = datetime(year=2022, month=4, day=4).date()
# input_date = datetime.today().date()
# mode = "Daily"
#
#
# print(min(datetime(year=2022, month=5, day=5).date(), datetime.today().date()))
#
# def isWeekend(date):
#     name = date.strftime("%A")
#     if name == "Sunday" or name == "Saturday":
#         return True
#     return False
#
# tmp_day = input_date
# count = 14
# while(count > 1):
#
#     if tmp_day.strftime("%Y-%m-%d") not in nse_holidays and not isWeekend(tmp_day):
#         print(f"{tmp_day.strftime('%Y-%m-%d')} - Not Holiday")
#         tmp_day -= timedelta(days=1)
#         count -= 1
#
#     else:
#         print(f"{tmp_day.strftime('%Y-%m-%d')} - Holiday")
#         tmp_day -= timedelta(days=1)
#
# print(tmp_day)
if __name__ == '__main__':
    data = pd.read_csv(r"nse holidays.csv", header=None, names=["date"])
    data['date'] = data['date'].apply(lambda x: datetime.strptime(x, "%d-%b-%y").date().strftime("%Y-%m-%d"))
    print(data.to_string())
    data.to_sql("nse_holidays", con=sqlite3.connect("stockdata.db"), if_exists="append", index=False)