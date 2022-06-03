import time
import numpy as np
import datetime
import pandas as pd
from utils import *
import multiprocessing as mp

def daily_batch_report(data):

    name, frame = data
    # print(f"{name} - Started")
    frame = frame[::-1].reset_index(drop=True)
    try:
        close = np.array(frame.loc[:, "close"])
        pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
        pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
        neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
        neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
        rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
        rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
        # print(f"{name} - Ended")
        if rs_1 <= 0.3:
            return (name, rs_1, "ls0.3")
        if rs_1 < 1 and rs_2 > 1:
            return (name, rs_1, "gr2ls1")
        if rs_1 > 1 and rs_2 < 1:
            return (name, rs_1, "ls2gr1")

    except IndexError as e:
        return (name, None, "insuf")
        # print(f"{e} Encountered. Halting procedure")

def thurs_weekly_batch_report(data):
    name, frame = data

    # print(name)
    frame = frame[::-1].reset_index(drop=True)
    date = frame.loc[0, "date"]
    dates = []
    count = 16
    while count > 0:
        try:
            if date.strftime("%A") != "Thursday":
                date -= datetime.timedelta(days=1)
            else:
                dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
                date -= datetime.timedelta(days=7)
                count -= 1
        except IndexError as e:
            return (name, None, "insuf")
            # print(f"{e} Encountered. Halting procedure")
    final_data = frame[frame['date'].isin(dates)].reset_index(drop=True)
    print(final_data)
    print(len(final_data))
    close = np.array(final_data.loc[:, "close"])
    if len(close) < 16:
        return (name, None, "insuf")

    pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
    pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
    neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
    neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
    rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
    rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
    roc_1 = round(close[0] / close[13], 2)
    roc_2 = round(close[1] / close[14], 2)

    if rs_1 <= 0.3:
        return (name, rs_1, "ls0.3")
    if rs_1 < 1 and rs_2 > 1:
        return (name, rs_1, "gr2ls1rs")
    if rs_1 > 1 and rs_2 < 1:
        return (name, rs_1, "ls2gr1rs")
    if roc_1 > 1 and roc_2 < 1:
        return (name, roc_1, "ls2gr1roc")
    if roc_1 < 1 and roc_2 > 1:
        return (name, roc_2, "gr2ls1roc")




def friday_weekly_batch_report(data):
    name, frame = data

    # print(name)
    frame = frame[::-1].reset_index(drop=True)
    date = frame.loc[0, "date"]
    dates = []
    count = 16
    while count > 0:
        try:
            if date.strftime("%A") != "Friday":
                date -= datetime.timedelta(days=1)
            else:
                dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
                date -= datetime.timedelta(days=7)
                count -= 1
        except IndexError as e:
            return (name, None, "insuf")
            # print(f"{e} Encountered. Halting procedure")
    final_data = frame[frame['date'].isin(dates)].reset_index(drop=True)
    print(final_data)
    print(len(final_data))
    close = np.array(final_data.loc[:, "close"])
    if len(close) < 16:
        return (name, None, "insuf")

    pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
    pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
    neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
    neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
    rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
    rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
    roc_1 = round(close[0] / close[13], 2)
    roc_2 = round(close[1] / close[14], 2)

    if rs_1 <= 0.3:
        return (name, rs_1, "ls0.3")
    if rs_1 < 1 and rs_2 > 1:
        return (name, rs_1, "gr2ls1rs")
    if rs_1 > 1 and rs_2 < 1:
        return (name, rs_1, "ls2gr1rs")
    if roc_1 > 1 and roc_2 < 1:
        return (name, roc_1, "ls2gr1roc")
    if roc_1 < 1 and roc_2 > 1:
        return (name, roc_2, "gr2ls1roc")

def get_batch_report():
    t1 = time.time()
    data = pd.read_sql(sql=selected_symbols_query, con=sqlite3.connect(dbpath), columns=["symbol", "date", "close"])
    data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y/%m/%d"))
    data = list(data.groupby("symbol"))
    # t1 = time.time()
    daily_lists = []
    thurs_lists = []
    friday_lists = []
    for d in data:
        daily_lists.append(daily_batch_report(d))
        thurs_lists.append(thurs_weekly_batch_report(d))
        friday_lists.append(friday_weekly_batch_report(d))

    print(daily_lists)
    print(thurs_lists)
    print(friday_lists)
    t2 = time.time()
    print(f"Time taken: {t2 - t1}")

if __name__ == '__main__':


    # t1 = time.time()
    # with mp.Pool() as pool:
    #     daily_dicts = pool.map(func=daily_batch_report, iterable=data)
    #     # thurs_dicts = pool.map(func=thurs_weekly_batch_report, iterable=data)
    #     # friday_dicts = pool.map(func=friday_weekly_batch_report, iterable=data)
    #
    # print(daily_dicts)
    # print(len(daily_dicts))
    # t2 = time.time()
    # print(f"Time taken: {t2-t1}")

    # t1 = time.time()
    get_batch_report()
    # t2 = time.time()
    # print(f"Time taken: {t2-t1}")
