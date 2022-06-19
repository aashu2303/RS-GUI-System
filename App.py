from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.list import IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.picker import MDDatePicker
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from plyer import filechooser
from kivy.uix.anchorlayout import AnchorLayout
import numpy as np
from utils import *

manager = ScreenManager()

Window.set_title("Trading Strategy Visualizer")
Window.maximize()
dpi = Window.dpi
width = Window.width
row_width = dp(width / 72 * 160 / dpi)
logged_in = False


class IconListItem(OneLineIconListItem):
    icon = StringProperty()


class StartScreen(Screen):

    def snapshot(self):
        print("NIFTY SNAPSHOT")

    def change_screen(self):
        if logged_in:
            self.manager.current = "maintain"
        else:
            self.manager.current = "password"
        self.manager.transition.direction = "left"

    def log(self, fp, title, list):
        fp.write(f"\n\t{title}\n")
        if not len(list):
            fp.write(f"\t\tNo symbols here\n")
        else:
            for i, sym in enumerate(list):
                if type(sym) == tuple and len(sym) == 2:
                    fp.write(f"\t\t{i + 1}. {sym[0]} - {sym[1]}\n")
                if type(sym) == tuple and len(sym) == 4:
                    fp.write(f"\t\t{i + 1}. {sym[0]}, {sym[1]}, {sym[2]}, {sym[3]}\n")
                elif type(sym) == str:
                    fp.write(f"\t\t{i + 1}. {sym}\n")

    def daily_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        RS_GR2 = []
        CLOSE_GR5 = []
        CLOSE_LS5 = []
        INSUF_DATA = set()
        for name, frame in data:
            frame = frame[::-1].reset_index(drop=True)
            try:
                close = np.array(frame.loc[:, "close"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
                rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
                if rs_1 > 2:
                    RS_GR2.append((name, rs_1))
                if pos_1[13] / close[0] >= 0.05:
                    CLOSE_GR5.append((name, close[0], pos_1[13], f"{round(pos_1[13] / close[0] * 100, 2)}%"))
                if neg_1[13] / close[0] >= 0.05:
                    CLOSE_LS5.append((name, close[0], neg_1[13], f"{round(neg_1[13] / close[0] * 100, 2)}%"))
            except IndexError as e:
                INSUF_DATA.add(name)
                # print(f"{e} Encountered. Halting procedure")
        return {"ls0.3": RS_LS0P3, "ls2gr1": RS_LS_TO_GR1, "gr2ls1": RS_HIGH_TO_LS1, "gr2": RS_GR2, "insuf": INSUF_DATA, "closegr5": CLOSE_GR5, "closels5": CLOSE_LS5}

    def thurs_weekly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        RS_GR2 = []
        INSUF_DATA = set()
        CLOSE_GR5 = []
        CLOSE_LS5 = []
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "date"]
            final_data = []
            count = 16
            while count > 0:
                try:
                    if date.strftime("%A") != "Thursday":
                        date -= datetime.timedelta(days=1)
                    else:
                        trading_date = previousTradingDay(date)
                        d = frame[frame['date'] == trading_date.strftime("%Y/%m/%d")].values
                        # print(d)
                        final_data.append(d[0])
                        date -= datetime.timedelta(days=7)
                        count -= 1
                except IndexError as e:
                    INSUF_DATA.add(name)
                    # print(f"{e} Encountered. Halting procedure")
                    count -= 1
            if len(final_data) >= 16:
                final_data = pd.DataFrame(final_data, columns=frame.columns)

                close = np.array(final_data.loc[:, "close"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
                rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
                roc_1 = round(close[0] / close[13], 2)
                roc_2 = round(close[1] / close[14], 2)

                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
                if roc_1 > 1 and roc_2 < 1:
                    ROC_LS_TO_GR1.append((name, roc_1))
                if roc_1 < 1 and roc_2 > 1:
                    ROC_HIGH_TO_LS1.append((name, roc_1))
                if rs_2 > 2:
                    RS_GR2.append((name, rs_1))
                if pos_1[13] / close[0] >= 0.05:
                    CLOSE_GR5.append((name, close[0], pos_1[13], f"{round(pos_1[13] / close[0] * 100, 2)}%"))
                if neg_1[13] / close[0] >= 0.05:
                    CLOSE_LS5.append((name, close[0], neg_1[13], f"{round(neg_1[13] / close[0] * 100, 2)}%"))

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "gr2": RS_GR2,
                "ls2gr1roc": ROC_LS_TO_GR1,
                "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA, "closegr5": CLOSE_GR5, "closels5": CLOSE_LS5}

    def friday_weekly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        RS_GR2 = []
        INSUF_DATA = set()
        CLOSE_GR5 = []
        CLOSE_LS5 = []
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "date"]
            final_data = []
            count = 16
            while count > 0:
                try:
                    if date.strftime("%A") != "Friday":
                        date -= datetime.timedelta(days=1)
                    else:
                        trading_date = previousTradingDay(date)
                        d = frame[frame['date'] == trading_date.strftime("%Y/%m/%d")].values
                        # print(d)
                        final_data.append(d[0])
                        date -= datetime.timedelta(days=7)
                        count -= 1
                except IndexError as e:
                    INSUF_DATA.add(name)
                    # print(f"{e} Encountered. Halting procedure")
                    count -= 1
            if len(final_data) >= 16:
                final_data = pd.DataFrame(final_data, columns=frame.columns)

                close = np.array(final_data.loc[:, "close"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
                rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
                roc_1 = round(close[0] / close[13], 2)
                roc_2 = round(close[1] / close[14], 2)

                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
                if roc_1 > 1 and roc_2 < 1:
                    ROC_LS_TO_GR1.append((name, roc_1))
                if roc_1 < 1 and roc_2 > 1:
                    ROC_HIGH_TO_LS1.append((name, roc_1))
                if rs_1 > 2:
                    RS_GR2.append((name, rs_1))
                if pos_1[13] / close[0] >= 0.05:
                    CLOSE_GR5.append((name, close[0], pos_1[13], f"{round(pos_1[13] / close[0] * 100, 2)}%"))
                if neg_1[13] / close[0] >= 0.05:
                    CLOSE_LS5.append((name, close[0], neg_1[13], f"{round(neg_1[13] / close[0] * 100, 2)}%"))

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "gr2": RS_GR2,
                "ls2gr1roc": ROC_LS_TO_GR1,
                "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA, "closegr5": CLOSE_GR5, "closels5": CLOSE_LS5}

    def monthly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        RS_GR2 = []
        INSUF_DATA = set()
        CLOSE_GR5 = []
        CLOSE_LS5 = []
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "date"]
            count = 16
            dates = list(map(lambda x: x.strftime("%Y/%m/%d"), lastndaysmonthly(date, freq=count)))
            final_data = frame[frame['date'].isin(dates)].reset_index(drop=True)
            print(final_data)
            if len(final_data) >= 16:
                close = np.array(final_data.loc[:, "close"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
                rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
                roc_1 = round(close[0] / close[13], 2)
                roc_2 = round(close[1] / close[14], 2)

                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
                if roc_1 > 1 and roc_2 < 1:
                    ROC_LS_TO_GR1.append((name, roc_1))
                if roc_1 < 1 and roc_2 > 1:
                    ROC_HIGH_TO_LS1.append((name, roc_1))
                if rs_1 > 2:
                    RS_GR2.append((name, rs_1))
                if pos_1[13] / close[0] >= 0.05:
                    CLOSE_GR5.append((name, close[0], pos_1[13], f"{round(pos_1[13] / close[0] * 100, 2)}%"))
                if neg_1[13] / close[0] >= 0.05:
                    CLOSE_LS5.append((name, close[0], neg_1[13], f"{round(neg_1[13] / close[0] * 100, 2)}%"))
            else:
                INSUF_DATA.add(name)

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "gr2": RS_GR2,
                "ls2gr1roc": ROC_LS_TO_GR1, "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA, "closegr5": CLOSE_GR5, "closels5": CLOSE_LS5}

    def quarterly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        RS_GR2 = []
        INSUF_DATA = set()
        CLOSE_GR5 = []
        CLOSE_LS5 = []
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "date"]
            count = 16
            dates = lastndaysquarterly(date, freq=count)
            final_data = frame[frame['date'].isin(dates)]
            if len(final_data) >= 16:
                close = np.array(final_data.loc[:, "close"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = round(np.sum(pos_1) / np.sum(neg_1), 2)
                rs_2 = round(np.sum(pos_2) / np.sum(neg_2), 2)
                roc_1 = round(close[0] / close[13], 2)
                roc_2 = round(close[1] / close[14], 2)

                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
                if roc_1 > 1 and roc_2 < 1:
                    ROC_LS_TO_GR1.append((name, roc_1))
                if roc_1 < 1 and roc_2 > 1:
                    ROC_HIGH_TO_LS1.append((name, roc_1))
                if rs_1 > 2:
                    RS_GR2.append((name, rs_1))
                if pos_1[13] / close[0] >= 0.05:
                    CLOSE_GR5.append((name, close[0], pos_1[13], f"{round(pos_1[13] / close[0] * 100, 2)}%"))
                if neg_1[13] / close[0] >= 0.05:
                    CLOSE_LS5.append((name, close[0], neg_1[13], f"{round(neg_1[13] / close[0] * 100, 2)}%"))
            else:
                INSUF_DATA.add(name)

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "gr2": RS_GR2,
                "ls2gr1roc": ROC_LS_TO_GR1, "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA, "closegr5": CLOSE_GR5, "closels5": CLOSE_LS5}

    def get_batch_report(self):
        cur = sqlite3.connect(dbpath).cursor()
        columns = ["symbol", "date", "close"]
        data = pd.DataFrame(cur.execute(selected_symbols_query), columns=columns)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.strptime(x, "%Y/%m/%d"))
        data = data.groupby("symbol")
        if not os.path.exists(report_dir_path):
            os.mkdir(report_dir_path)
        filename = rf"BatchReport - {lastTradingDay(dbpath).strftime('%Y-%m-%d')}.txt"

        daily_lists = self.daily_batch_report(data)
        thursday_lists = self.thurs_weekly_batch_report(data)
        friday_lists = self.friday_weekly_batch_report(data)
        monthly_lists = self.monthly_batch_report(data)
        quarterly_lists = self.quarterly_batch_report(data)

        filepath = os.path.join(report_dir_path, filename)
        try:
            fp = open(filepath, "w")
            fp.write(
                f"*** Batch Report for the {len(data)} Symbols - {datetime.datetime.today().date().strftime('%Y/%m/%d')} ***\n")
            fp.write(f"\nDAILY RS")
            self.log(fp=fp, title="CATEGORY: Daily RS < 0.3 - BULLISH VIEW", list=daily_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: RS Moving above 1 - BULLISH VIEW", list=daily_lists['ls2gr1'])
            self.log(fp=fp, title="CATEGORY: RS Moving below 1 - BEARISH VIEW", list=daily_lists['gr2ls1'])
            self.log(fp=fp, title="CATEGORY: Daily RS > 2 - BEARISH VIEW", list=daily_lists['gr2'])
            self.log(fp=fp, title="CATEGORY: CLOSE > 5% - BULLISH VIEW", list=daily_lists['closegr5'])
            self.log(fp=fp, title="CATEGORY: CLOSE < 5% - BEARISH VIEW", list=daily_lists['closels5'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=daily_lists['insuf'])
            fp.write(f"\nWEEKLY - THURSDAY RS")
            self.log(fp=fp, title="CATEGORY: Weekly RS < 0.3 - BULLISH VIEW", list=thursday_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Weekly RS Moving above 1 - BULLISH VIEW",
                     list=thursday_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Weekly RS Moving below 1 - BEARISH VIEW",
                     list=thursday_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Weekly RS > 2 - BEARISH VIEW", list=thursday_lists['gr2'])
            self.log(fp=fp, title="CATEGORY: Weekly ROC Moving above 1 - BULLISH VIEW",
                     list=thursday_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Weekly ROC Moving below 1 - BEARISH VIEW",
                     list=thursday_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: CLOSE > 5% - BULLISH VIEW", list=thursday_lists['closegr5'])
            self.log(fp=fp, title="CATEGORY: CLOSE < 5% - BEARISH VIEW", list=thursday_lists['closels5'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=thursday_lists['insuf'])
            fp.write(f"\nWEEKLY - FRIDAY RS")
            self.log(fp=fp, title="CATEGORY: Weekly RS < 0.3 - BULLISH VIEW", list=friday_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Weekly RS Moving above 1 - BULLISH VIEW", list=friday_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Weekly RS Moving below 1 - BEARISH VIEW", list=friday_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Weekly RS > 2 - BEARISH VIEW", list=friday_lists['gr2'])
            self.log(fp=fp, title="CATEGORY: Weekly ROC Moving above 1 - BULLISH VIEW",
                     list=friday_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Weekly ROC Moving below 1 - BEARISH VIEW",
                     list=friday_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: CLOSE > 5% - BULLISH VIEW", list=friday_lists['closegr5'])
            self.log(fp=fp, title="CATEGORY: CLOSE < 5% - BEARISH VIEW", list=friday_lists['closels5'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=friday_lists['insuf'])
            fp.write(f"\nMONTHLY RS")
            self.log(fp=fp, title="CATEGORY: Monthly RS < 0.3 - BULLISH VIEW", list=monthly_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Monthly RS Moving above 1 - BULLISH VIEW",
                        list=monthly_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Monthly RS Moving below 1 - BEARISH VIEW",
                        list=monthly_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Monthly RS > 2 - BEARISH VIEW", list=monthly_lists['gr2'])
            self.log(fp=fp, title="CATEGORY: Monthly ROC Moving above 1 - BULLISH VIEW",
                        list=monthly_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Monthly ROC Moving below 1 - BEARISH VIEW",
                        list=monthly_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: CLOSE > 5% - BULLISH VIEW", list=monthly_lists['closegr5'])
            self.log(fp=fp, title="CATEGORY: CLOSE < 5% - BEARISH VIEW", list=monthly_lists['closels5'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=monthly_lists['insuf'])
            fp.write(f"\nQUARTERLY RS")
            self.log(fp=fp, title="CATEGORY: Quarterly RS < 0.3 - BULLISH VIEW", list=quarterly_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Quarterly RS Moving above 1 - BULLISH VIEW",
                        list=quarterly_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Quarterly RS Moving below 1 - BEARISH VIEW",
                        list=quarterly_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Quarterly RS > 2 - BEARISH VIEW", list=quarterly_lists['gr2'])
            self.log(fp=fp, title="CATEGORY: Quarterly ROC Moving above 1 - BULLISH VIEW",
                        list=quarterly_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Quarterly ROC Moving below 1 - BEARISH VIEW",
                        list=quarterly_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: CLOSE > 5% - BULLISH VIEW", list=quarterly_lists['closegr5'])
            self.log(fp=fp, title="CATEGORY: CLOSE < 5% - BEARISH VIEW", list=quarterly_lists['closels5'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=quarterly_lists['insuf'])
            fp.close()
            print("Batch Report creation successful")
            popup = MDDialog(
                title="Batch Report",
                type="confirmation",
                text=f"Batch Report created at {filepath}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: popup.dismiss()
                    )
                ]
            )
            popup.open()
            return True
        except Exception as e:
            print(e)
            print("Batch Report creation unsuccessful")
            return False


class MaintainScreen(Screen):

    def updateDb(self, dbpath):
        dbconn = sqlite3.connect(dbpath)
        lastday = lastTradingDay(dbpath)
        nofiles = []
        if lastday == previousTradingDay(datetime.datetime.today().date()):
            popup = MDDialog(
                title="Data Up-to-date",
                text="Data is up-to-date",
                size_hint=(.5, .5),
                buttons=[
                    MDFlatButton(
                        text="Cancel",
                        on_release=lambda x: popup.dismiss()
                    )
                ]
            )
            popup.open()
        else:
            while lastday < previousTradingDay(datetime.datetime.today().date()):
                lastday += datetime.timedelta(days=1)
                if lastday.strftime("%Y/%m/%d") not in nse_holidays:
                    filepath = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + bhavfilename)
                    csvfile = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + "-NSE-EQ.csv")

                    try:
                        os.rename(filepath, csvfile)
                    except FileNotFoundError:
                        nofiles.append(lastday.strftime("%Y-%m-%d"))
                        continue

                    data = pd.read_csv(csvfile, delimiter=",",
                                       names=["symbol", "date", "open", "high", "low", "close", "volume", "openI"])[
                        ["symbol", "date", "close"]]
                    data['date'] = data['date'].apply(lambda x: f"{str(x)[:4]}/{str(x)[4:6]}/{str(x)[6:8]}")
                    data = data[data['symbol'].isin(symbols)]
                    try:
                        data.to_sql(name="stocks", con=dbconn, if_exists="append", index=False)
                    except sqlite3.IntegrityError as e:
                        print(f"{e} occured")
            if len(nofiles) > 0:
                text = f"The files corresponding to following dates were not found:\n{nofiles}"
                popup = MDDialog(
                    title="Files not found",
                    text=text,
                    size=(0.5, 0.5),
                    buttons=[
                        MDFlatButton(
                            text="Cancel",
                            on_release=lambda x: popup.dismiss()
                        )
                    ]
                )
                popup.open()

    def updateSymbols(self):
        file = filechooser.open_file()

        print(file)

    def updateHolidays(self):
        file = filechooser.open_file()
        print(file)


class InputScreen(Screen):
    menu = None
    table_set = False
    # print("Entered Input Screen")
    timeperiods = ["Daily", "Weekly - Monday", "Weekly - Tuesday", "Weekly - Wednesday", "Weekly - Thursday",
                   "Weekly - Friday", "Monthly", "Quarterly"]
    previous_date = None
    next_date = None
    button_layout = None
    symbol_now = None
    next_symbol = None
    prev_symbol = None
    startdate_now = None
    timeperiod_now = None
    frequency_now = None

    def set_menu(self):
        selected_symbols = symbols
        if not self.ids['drop_item'].text.isspace():
            selected_symbols = [sym for sym in symbols if self.ids['drop_item'].text.upper() in sym.upper()]
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "currency-inr",
                "height": dp(56),
                "text": sym,
                "on_release": lambda x=sym: self.set_item(x, "drop_item"),

            } for sym in selected_symbols]

        if self.menu:
            self.menu.dismiss()
            self.menu = None

        self.menu = MDDropdownMenu(
            caller=self.ids['drop_item'],
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.menu.open()

    def set_item(self, item, id):
        self.ids[id].text = item
        self.menu.dismiss()

    def on_save(self, instance, value, date_range):
        self.ids['start_date_input'].text = str(value)
        self.ids['start_date_input'].error = False
        self.ids['start_date_input'].helper_text = "Valid Date"

    def date_picker(self):
        todate = datetime.datetime.today().date()
        date_dialog = MDDatePicker(year=todate.year, month=todate.month, day=todate.day)
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def tp_expand(self):
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "timer",
                "text": sym,
                "height": dp(56),
                "on_release": lambda x=sym: self.set_item(x, "tp_drop"),
            } for sym in self.timeperiods
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids['tp_drop'],
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.menu.bind()
        self.menu.open()

    def slider_val(self, value):
        self.ids['frequency_input'].text = str(value)

    def validate(self):
        symbol = self.ids['drop_item'].text
        timeperiod = self.ids['tp_drop'].text
        frequency = int(self.ids['frequency_input'].text)
        if symbol not in symbols:
            popup = MDDialog(
                title="Invalid Symbol",
                text="Select a valid symbol or ticker",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Error",
                        on_release=lambda x: popup.dismiss()
                    )
                ],
                type="alert"
            )
            popup.open()
            return False

        try:
            startdate = datetime.datetime.strptime(self.ids['start_date_input'].text, "%Y-%m-%d").date()
            if startdate > lastTradingDay(dbpath):
                popup = MDDialog(
                    title="Invalid Date",
                    text="Cannot calculate the RS table for days after last trading day",
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Error",
                            on_release=lambda x: popup.dismiss()
                        )
                    ],
                    type="alert"
                )
                popup.open()
                return False
            elif startdate > lastndaysdaily(lastTradingDay(dbpath), frequency):
                popup = MDDialog(
                    title="Insufficient datapoints",
                    text=f"Select a date before {lastndaysdaily(lastTradingDay(dbpath), frequency).strftime('%Y-%m-%d')}",
                    buttons=[
                        MDFlatButton(
                            text="CANCEL",
                            theme_text_color="Error",
                            on_release=lambda x: popup.dismiss()
                        )
                    ],
                    type="alert"
                )
                popup.open()
                return False

        except ValueError:
            startdate = None

        if timeperiod not in self.timeperiods:
            popup = MDDialog(
                title="Invalid TimePeriod",
                text=f"Select a valid time period - Daily/Weekday",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Error",
                        on_release=lambda x: popup.dismiss()
                    )
                ],
                type="alert"
            )
            popup.open()
            return False

        self.symbol_now = symbol
        self.next_symbol = symbols[(symbols.index(symbol) + 1) % len(symbols)]
        self.prev_symbol = symbols[(symbols.index(symbol) - 1) % len(symbols)]
        self.timeperiod_now = timeperiod
        self.frequency_now = frequency
        if startdate is None:
            self.startdate_now = lastTradingDay(dbpath)
            self.build(symbol=symbol, timeperiod=timeperiod, frequency=frequency)
        else:
            self.startdate_now = startdate
            self.build(symbol=symbol, startdate=startdate, timeperiod=timeperiod, frequency=frequency)

    def get_data(self, symbol, startdate, timeperiod, frequency):
        db_conn = sqlite3.connect(database=dbpath)
        cur = db_conn.cursor()

        # data["DATE"] = data["DATE"].apply(lambda x: datetime.datetime.strptime(x, "%Y/%m/%d").date())
        # startdate = datetime.datetime.strptime(settings['startdate'], "%Y-%m-%d").date()
        if timeperiod == "Daily":
            dates = []
            date = startdate
            count = 2 * frequency
            while count > 0:
                if isHoliday(date):
                    date -= datetime.timedelta(days=1)
                else:
                    dates.append(date.strftime("%Y/%m/%d"))
                    date -= datetime.timedelta(days=1)
                    count -= 1
            dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
            data = pd.DataFrame(
                cur.execute(f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol=:sym order by date",
                            {"sym": symbol}).fetchall(), columns=columns)
            # print(data)
            # print(len(data))
            final_data = self.process(data, frequency=frequency)
            return final_data

        elif "Weekly" in timeperiod:
            day = timeperiod.split(" - ")[-1]
            dates = []
            date = startdate
            count = 2 * frequency
            while count > 0:
                if date.strftime("%A") == day:
                    dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
                    date -= datetime.timedelta(days=7)
                    count -= 1
                else:
                    date -= datetime.timedelta(days=1)
            dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
            data = pd.DataFrame(
                cur.execute(f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol=:sym order by date",
                            {"sym": symbol}).fetchall(), columns=columns)

            final_data = self.process(data, frequency=frequency)
            return final_data

        elif timeperiod == "Monthly":
            dates = lastndaysmonthly(startdate, 2 * frequency)
            dates = list(map(lambda x: x.strftime("%Y/%m/%d"), dates))
            # print(dates)
            data = pd.DataFrame(
                cur.execute(f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol=:sym order by date",
                            {"sym": symbol}).fetchall(), columns=columns)
            final_data = self.process(data, frequency=frequency)
            # print(final_data)
            return final_data

        elif timeperiod == "Quarterly":
            dates = lastndaysquarterly(startdate, 2 * frequency)
            dates = list(map(lambda x: x.strftime("%Y/%m/%d"), dates))
            # print(dates)
            data = pd.DataFrame(
                cur.execute(f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol=:sym order by date",
                            {"sym": symbol}).fetchall(), columns=columns)
            final_data = self.process(data, frequency=frequency)
            return final_data

    def process(self, data, frequency):

        data['roc'] = pd.Series(np.zeros(len(data)))
        for i in range(len(data)):
            if i < frequency:
                data.loc[i, 'roc'] = np.nan
            else:
                data.loc[i, 'roc'] = round(data.loc[i, 'close'] / data.loc[i - frequency + 1, 'close'], 2)

        data['pos'] = pd.Series(map(lambda x: round(max(0, x), 2), data['close'].diff(periods=1)))
        data['neg'] = pd.Series(map(lambda x: round(max(0, -x), 2), data['close'].diff(periods=1)))
        data['cldiff'] = pd.Series(map(lambda x: 1 if x > 0 else 0, data['close'].diff(periods=1)))
        data['last n pos'] = data.loc[1:, 'pos'].rolling(window=frequency).sum().apply(lambda x: round(x, 2))
        data['last n neg'] = data.loc[1:, 'neg'].rolling(window=frequency).sum().apply(lambda x: round(x, 2))
        data = data.dropna().reset_index(drop=True)
        data['rs'] = pd.Series(map(lambda x: round(x, 2), data['last n pos'] / data['last n neg']))
        data['rsdiff'] = pd.Series(map(lambda x: 1 if x > 0 else 0, data['rs'].diff(periods=1)))
        # print(data.to_string())
        return data[['date', 'cldiff', 'close', 'pos', 'neg', 'last n pos', 'last n neg', 'rsdiff', 'rs', 'roc']]

    def build(self, symbol, timeperiod, frequency, startdate=lastTradingDay(dbpath)):
        stock_data = self.get_data(symbol, startdate, timeperiod, frequency)
        # print(stock_data)
        if self.timeperiod_now == "Daily":
            self.previous_date = previousTradingDay(
                datetime.datetime.strptime(stock_data.loc[0, 'date'], "%Y/%m/%d").date() - datetime.timedelta(days=1))
            self.next_date = nextndaysdaily(
                datetime.datetime.strptime(stock_data.loc[len(stock_data) - 1, 'date'], "%Y/%m/%d").date(),
                self.frequency_now)
        elif "Weekly" in self.timeperiod_now:
            self.previous_date = previousTradingDay(
                datetime.datetime.strptime(stock_data.loc[0, 'date'], "%Y/%m/%d").date() - datetime.timedelta(days=7))
            self.next_date = nextndaysweekly(datetime.datetime.strptime(stock_data.loc[len(stock_data) - 1, 'date'],
                                                                        "%Y/%m/%d").date() + datetime.timedelta(days=7),
                                             self.frequency_now)
        elif self.timeperiod_now == "Monthly":
            self.previous_date = previousmonthEnd(
                datetime.datetime.strptime(stock_data.loc[0, 'date'], "%Y/%m/%d").date())
            next_date_tmp = datetime.datetime.strptime(stock_data.loc[len(stock_data) - 1, 'date'], "%Y/%m/%d").date()
            self.next_date = nextndaysmonthly(next_date_tmp, self.frequency_now)

        elif self.timeperiod_now == "Quarterly":
            self.previous_date = previousquarterEnd(
                datetime.datetime.strptime(stock_data.loc[0, 'date'], "%Y/%m/%d").date())
            next_date_tmp = datetime.datetime.strptime(stock_data.loc[len(stock_data) - 1, 'date'], "%Y/%m/%d").date()
            self.next_date = nextndaysquarterly(next_date_tmp, self.frequency_now)

        self.refresh_view(stock_data)

    def get_divergence(self, cldiffflag, rsdiffflag):
        if (cldiffflag == rsdiffflag):
            return ' '
        elif (cldiffflag == 1):
            return 'minus'
        else:
            return 'plus'

    def create_data(self, stock_data):
        dates = stock_data["date"].to_list()
        cols = stock_data.columns.to_list()
        # print(dates)

        table_data = []
        col_data = []
        for c in cols:
            if (c == 'rsdiff' or c == 'cldiff'):
                continue
            tmp_lbl = MDLabel(text=c.upper())
            tmp_lbl.size_hint_y = None
            tmp_lbl.height = 40
            tmp_lbl.line_width = 1
            tmp_lbl.halign = "center"
            tmp_lbl.md_bg_color = (.85, .80, .30, 0.8)
            tmp_lbl.line_color = (0, 0, 0, 1)
            col_data.append(tmp_lbl)
        table_data.append(col_data)

        for i in range(len(dates)):
            row_data = []
            cldiffflag = -1
            rsdiffflag = -1
            for c in cols:
                if c == 'cldiff':
                    cldiffflag = stock_data.loc[i, c]
                    continue
                elif c == 'rsdiff':
                    rsdiffflag = stock_data.loc[i, c]
                    continue

                elif c == 'rs':
                    divergence = self.get_divergence(cldiffflag, rsdiffflag)
                    tmp_lbl = MDBoxLayout(line_color=(0, 0, 0, 1))
                    list_item = OneLineAvatarIconListItem(divider='Inset')
                    list_item.height = 30
                    if divergence != ' ':
                        div_icon = IconRightWidget(icon=divergence)
                        list_item.add_widget(div_icon)
                    lbl = MDLabel(text=str(stock_data.loc[i, c]), halign='right')
                    tmp_lbl.add_widget(lbl)
                    tmp_lbl.add_widget(list_item)

                    if i in [len(dates) - 14, len(dates) - 13, len(dates) - 12]:
                        list_item.bg_color = (.85, .30, .30, 0.5)
                        lbl.md_bg_color = (.85, .30, .30, 0.5)
                    if i == np.argmax(stock_data['rs']):
                        list_item.bg_color = (1, 0, 0, 1)
                        lbl.md_bg_color = (1, 0, 0, 1)
                    elif i == np.argmin(stock_data['rs']):
                        list_item.bg_color = (0, 1, 0, 1)
                        lbl.md_bg_color = (0, 1, 0, 1)
                    if i > 0:
                        if stock_data.loc[i, c] > 1 and stock_data.loc[i - 1, c] < 1:
                            list_item.bg_color = (.30, 1, .30, 0.5)
                            lbl.md_bg_color = (.30, 1, .30, 0.5)
                        elif stock_data.loc[i, c] < 1 and stock_data.loc[i - 1, c] > 1:
                            list_item.bg_color = (1, .30, .30, 0.5)
                            lbl.md_bg_color = (1, .30, .30, 0.5)

                if c != 'rs':
                    tmp_lbl = MDLabel(text=str(stock_data.loc[i, c]))
                    tmp_lbl.halign = "center"
                    tmp_lbl.size_hint_y = None
                    tmp_lbl.height = 30
                    tmp_lbl.line_width = 1
                    tmp_lbl.line_color = (0, 0, 0, 0.5)
                    if i in [len(dates) - 14, len(dates) - 13, len(dates) - 12]:
                        tmp_lbl.md_bg_color = (.85, .30, .30, 0.5)

                row_data.append(tmp_lbl)
            table_data.append(row_data)

        return np.array(table_data, dtype=object).flatten(), cols, dates

    def refresh_view(self, data):
        data, cols, dates = self.create_data(data)
        table_obj = self.ids['table_box']
        button_obj = self.ids['button_layout']

        if self.table_set:
            table_obj.clear_widgets()
            button_obj.clear_widgets()

        table_obj.cols = len(cols) - 2
        table_obj.rows = len(dates) + 1
        for lbl in data:
            table_obj.add_widget(lbl)

        # print(len(data))
        # print(len(cols))
        # print(len(dates)+1)
        # assert len(data) == len(cols) * (len(dates)+1)

        # button_obj.rows = 2
        # button_obj.cols = 2
        b1 = MDRectangleFlatButton(text="Previous Frame", pos_hint={"center_x": 0.3, "center_y": 0.7}, font_style="H5",
                                   on_release=lambda _: self.alter_tables(symbol=self.symbol_now,
                                                                          startdate=self.previous_date,
                                                                          timeperiod=self.timeperiod_now,
                                                                          frequency=self.frequency_now))
        b2 = MDRectangleFlatButton(text="Next Frame", pos_hint={"center_x": 0.7, "center_y": 0.7}, font_style="H5",
                                   on_release=lambda _: self.alter_tables(symbol=self.symbol_now,
                                                                          startdate=self.next_date,
                                                                          timeperiod=self.timeperiod_now,
                                                                          frequency=self.frequency_now))
        b3 = MDRectangleFlatButton(text="Previous Symbol", pos_hint={"center_x": 0.3, "center_y": 0.3}, font_style="H5",
                                   on_press=lambda _: self.alter_tables(symbol=self.prev_symbol,
                                                                        startdate=self.startdate_now,
                                                                        timeperiod=self.timeperiod_now,
                                                                        frequency=self.frequency_now))
        b4 = MDRectangleFlatButton(text="Next Symbol", pos_hint={"center_x": 0.7, "center_y": 0.3}, font_style="H5",
                                   on_press=lambda _: self.alter_tables(symbol=self.next_symbol,
                                                                        startdate=self.startdate_now,
                                                                        timeperiod=self.timeperiod_now,
                                                                        frequency=self.frequency_now))
        if self.symbol_now == symbols[0]:
            b3.disabled = True
        else:
            b3.disabled = False

        if self.symbol_now == symbols[-1]:
            b4.disabled = True

        else:
            b4.disabled = False

        if self.startdate_now == lastTradingDay(dbpath):
            b2.disabled = True
        else:
            b2.disabled = False
        button_obj.add_widget(b1)
        button_obj.add_widget(b2)
        button_obj.add_widget(b3)
        button_obj.add_widget(b4)
        self.table_set = True

    def alter_tables(self, symbol, startdate, timeperiod, frequency):
        self.prev_symbol = symbols[(symbols.index(symbol) - 1) % len(symbols)]
        self.symbol_now = symbol
        self.next_symbol = symbols[(symbols.index(symbol) + 1) % len(symbols)]
        self.ids['drop_item'].text = symbol
        if timeperiod == "Daily":
            self.previous_date = lastndaysdaily(startdate, frequency)
            self.next_date = nextndaysdaily(startdate, frequency)
        elif 'Weekly' in timeperiod:
            day = timeperiod.split(" - ")[-1]
            self.previous_date = lastndaysweekly(startdate, frequency, day)
            self.next_date = nextndaysweekly(startdate, frequency)
        self.startdate_now = startdate
        self.timeperiod_now = timeperiod
        self.frequency_now = frequency
        self.build(symbol=symbol, startdate=startdate, timeperiod=timeperiod, frequency=frequency)


class PasswordScreen(Screen):

    def check_login(self):
        login_widget = self.ids["pslogin"]
        # # print(login)
        if len(login_widget.text) > 0:
            login_widget.helper_text = "Valid Login ID"
            login_widget.error = False
            login_widget.helper_text_mode = "on_focus"
        else:
            login_widget.error = True
            login_widget.helper_text = "Invalid Login ID"
            login_widget.helper_text_mode = "on_error"

    def check_pass(self):
        password_widget = self.ids["pspassword"]
        password = password_widget.text
        if any(c in '''!@#$%^&*()_-+={[}]:;'"<,>.?/`~''' for c in password) and any(c.isnumeric() for c in password) \
                and any(c.isupper() for c in password) and len(password) >= 8:
            password_widget.helper_text = "Valid Password"
            password_widget.helper_text_mode = "persistent"
            password_widget.error = False
        else:
            helper_text = "Password should have atleast "
            errors = []
            if not any(c in '''!@#$%^&*()_-+={[}]:;'"<,>.?/`~''' for c in password):
                errors.append("1 special character")
            if not any(c.isnumeric() for c in password):
                errors.append("1 numeric character")
            if not any(c.isupper() for c in password):
                errors.append("1 uppercase character")
            if len(password) < 8:
                errors.append("8 characters")

            password_widget.helper_text = helper_text + ", ".join(errors)
            password_widget.error = True
            password_widget.helper_text_mode = "on_error"

    def submit(self):
        login_id = self.ids["pslogin"].text
        pass_id = self.ids["pspassword"].text
        if login_id == LOGIN and pass_id == PASSWORD:
            print("Passwords and Login matched")
            global logged_in
            logged_in = True
            self.manager.current = "maintain"
            self.manager.transition.direction = "left"


class IndexPopup(BoxLayout):
    menu = None
    index_name = None

    def index_dd(self):
        selected_indices = indices
        if not self.ids['index_input'].text.isspace():
            selected_indices = [sym for sym in indices if self.ids['index_input'].text.upper() in sym.upper()]
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "currency-inr",
                "height": dp(56),
                "text": sym,
                "on_release": lambda x=sym: self.set_item(x, "index_input"),

            } for sym in selected_indices]

        if self.menu:
            self.menu.dismiss()
            self.menu = None

        self.menu = MDDropdownMenu(
            caller=self.ids['index_input'],
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.menu.open()

    def set_item(self, item, id):
        self.ids[id].text = item
        self.index_name = item
        self.menu.dismiss()


class SnapshotScreen(Screen):
    menu = None
    previous_index = None
    index_now = None
    next_index = None
    popup = None
    index_input = None
    table_set = False

    def get_data(self, symbols, startdate, timeperiod, frequency):
        db_conn = sqlite3.connect(database=dbpath)
        cur = db_conn.cursor()

        if timeperiod == "Daily":
            dates = []
            date = startdate
            count = 2 * frequency
            while count > 0:
                if isHoliday(date):
                    date -= datetime.timedelta(days=1)
                else:
                    dates.append(date.strftime("%Y/%m/%d"))
                    date -= datetime.timedelta(days=1)
                    count -= 1
            dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
            data = pd.DataFrame(
                cur.execute(
                    f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol in {tuple(symbols)} order by date").fetchall(),
                columns=columns)

            return data

        elif "Weekly" in timeperiod:
            day = timeperiod.split(" - ")[-1]
            dates = []
            date = startdate
            count = 2 * frequency
            while count > 0:
                if date.strftime("%A") == day:
                    dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
                    date -= datetime.timedelta(days=7)
                    count -= 1
                else:
                    date -= datetime.timedelta(days=1)
            dates.append(previousTradingDay(date).strftime("%Y/%m/%d"))
            data = pd.DataFrame(
                cur.execute(
                    f"SELECT * FROM stocks WHERE date in {tuple(dates)} and symbol in {tuple(symbols)} order by date").fetchall(),
                columns=columns)

            return data

    def process(self, data, frequency):
        data['pos'] = pd.Series(map(lambda x: round(max(0, x), 2), data['close'].diff(periods=1)))
        data['neg'] = pd.Series(map(lambda x: round(max(0, -x), 2), data['close'].diff(periods=1)))
        data['last n pos'] = data.loc[1:, 'pos'].rolling(window=frequency).sum().apply(lambda x: round(x, 2))
        data['last n neg'] = data.loc[1:, 'neg'].rolling(window=frequency).sum().apply(lambda x: round(x, 2))
        data = data.dropna().reset_index(drop=True)
        data['rs'] = pd.Series(map(lambda x: round(x, 2), data['last n pos'] / data['last n neg']))
        # print(data.to_string())
        return data[['symbol', 'close', 'pos', 'neg', 'rs']]

    def on_enter(self, *args):
        index_input = IndexPopup()
        self.popup = MDDialog(
            title="Enter an index symbol",
            type="custom",
            content_cls=index_input,
            size_hint=(0.8, 0.8),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda _: self.cancel_snap(),
                ),
                MDFlatButton(
                    text="OK",
                    on_release=lambda _: self.get_snapshot(),
                ),
            ],
        )
        self.index_input = index_input
        self.popup.open()

    def cancel_snap(self):
        if self.popup:
            self.popup.dismiss()
        self.manager.current = "start"
        self.manager.transition.direction = "right"

    def validate(self):

        index = self.index_input.index_name
        if index not in indices:
            popup = MDDialog(
                title="Invalid Index",
                text="Index not found in the list",
                size_hint=(.5, .4),
                buttons=[
                    MDFlatButton(
                        text="CLOSE", on_release=lambda x: popup.dismiss()
                    )
                ]
            )
            popup.open()
            return True

        self.index_now = index
        self.previous_index = indices[(indices.index(index) - 1) % len(indices)]
        self.next_index = indices[(indices.index(index) + 1) % len(indices)]
        return False

    def get_snapshot(self):
        if self.popup:
            self.popup.dismiss()
        # self.manager.current = "start"
        # self.manager.transition.direction = "right"
        self.validate()
        components = sqlite3.connect(dbpath).cursor().execute(components_query, {"index": self.index_now}).fetchall()
        components = list(map(lambda x: x[0], components))
        index = self.index_now
        components.append(index)
        daily_data = self.get_data(components, lastTradingDay(dbpath), "Daily", 14)
        daily_data = daily_data.groupby('symbol')
        daily_index_data = self.process(daily_data.get_group(index).reset_index(drop=True), 14).loc[1:, :].reset_index(
            drop=True)
        # print("Daily Index Data")
        # print(daily_index_data)
        daily_components_data = [daily_data.get_group(x).reset_index(drop=True) for x in components if x != index]
        for i in range(len(daily_components_data)):
            daily_components_data[i] = self.process(daily_components_data[i], 14)
            daily_components_data[i] = daily_components_data[i].loc[len(daily_components_data[i]) - 3:, :].reset_index(
                drop=True)
            # print(frame)

        thurs_data = self.get_data(components, lastTradingDay(dbpath), "Weekly - Thursday", 14)
        thurs_data = thurs_data.groupby('symbol')
        thurs_index_data = self.process(thurs_data.get_group(index).reset_index(drop=True), 14).loc[1:, :].reset_index(
            drop=True)
        # print("Thursday Index Data")
        # print(thurs_index_data)
        thurs_components_data = [thurs_data.get_group(x).reset_index(drop=True) for x in components if x != index]
        for i in range(len(thurs_components_data)):
            thurs_components_data[i] = self.process(thurs_components_data[i], 14)
            thurs_components_data[i] = thurs_components_data[i].loc[len(thurs_components_data[i]) - 3:, :].reset_index(
                drop=True)
            # print(frfri_components_data[i]
        fri_data = self.get_data(components, lastTradingDay(dbpath), "Weekly - Friday", 14)
        fri_data = fri_data.groupby('symbol')
        fri_index_data = self.process(fri_data.get_group(index).reset_index(drop=True), 14).loc[1:, :].reset_index(
            drop=True)
        # print("Friday Index Data")
        # print(fri_index_data)
        fri_components_data = [fri_data.get_group(x).reset_index(drop=True) for x in components if x != index]
        for i in range(len(fri_components_data)):
            fri_components_data[i] = self.process(fri_components_data[i], 14)
            fri_components_data[i] = fri_components_data[i].loc[len(fri_components_data[i]) - 3:, :].reset_index(
                drop=True)
            # print(frame)

        table_data, comp_data = self.create_data(index_daily=daily_index_data, index_thurs=thurs_index_data,
                                                 index_fri=fri_index_data, comps_daily=daily_components_data,
                                                 comps_thurs=thurs_components_data, comps_fri=fri_components_data)

        self.refresh_view(table_data, comp_data)
        # print(table_data)
        # print(len(table_data))
    def get_divergence(self, cldiffflag, rsdiffflag):
        if (cldiffflag == rsdiffflag):
            return ' '
        elif (cldiffflag == 1):
            return 'minus'
        else:
            return 'plus'

    def create_data(self, index_daily, index_thurs, index_fri, comps_daily, comps_thurs, comps_fri):
        heading_height = 26
        row_height = 20

        def create_label(text, height, linewidth=1, md_bg_color=(1, 1, 1, 1), line_color=(0, 0, 0, 1)):
            label = MDLabel(text=text.upper())
            label.size_hint_y = None
            label.height = height
            label.line_color = line_color
            label.line_width = linewidth
            label.halign = "center"
            label.md_bg_color = md_bg_color
            return label

        index_name = self.index_now
        table_data = []
        col_data = []
        cols1 = [index_name, "DAILY", "DAILY", "DAILY", "THURSDAY", "THURSDAY", "THURSDAY", "FRIDAY", "FRIDAY",
                 "FRIDAY", " "]
        cols2 = ["DAILY CLOSE", "POS", "NEG", "RS", "POS", "NEG", "RS", "POS", "NEG", "RS", "WEEKLY CLOSE"]

        for c in cols1:
            if (c == 'rsdiff' or c == 'cldiff'):
                continue
            tmp_lbl = MDLabel(text=c.upper())
            tmp_lbl.size_hint_y = None
            tmp_lbl.height = 40
            tmp_lbl.line_width = 1
            tmp_lbl.halign = "center"
            tmp_lbl.md_bg_color = (.85, .80, .30, 0.8)
            tmp_lbl.line_color = (0, 0, 0, 1)
            col_data.append(tmp_lbl)
        table_data.append(col_data)

        col_data = []
        for c in cols2:
            if (c == 'rsdiff' or c == "cldiff"):
                continue
            tmp_lbl = MDLabel(text=c.upper())
            tmp_lbl.size_hint_y = None
            tmp_lbl.height = 40
            tmp_lbl.line_width = 1
            tmp_lbl.halign = "center"
            tmp_lbl.md_bg_color = (.85, .80, .30, 0.8)
            tmp_lbl.line_color = (0, 0, 0, 1)
            col_data.append(tmp_lbl)
        table_data.append(col_data)

        master_table_data = []
        for i, dataframe in enumerate([index_daily, index_thurs, index_fri]):
            if i == 0:
                dataframe = dataframe[['close', "pos", "neg", "rs"]]
                data = index_daily
            elif i == 1:
                dataframe = dataframe[['pos', 'neg', "rs"]]
                data = index_thurs
            elif i == 2:
                dataframe = dataframe[['pos', 'neg', "rs", "close"]]
                data = index_fri
            else:
                data = None
            cols = dataframe.columns
            length = len(dataframe)
            tmp_data = []
            for i in range(len(dataframe)):
                row_data = []
                cldiffflag = -1
                rsdiffflag = -1
                for c in cols:
                    if c == 'rs':
                        tmp_lbl = MDBoxLayout(line_color=(0, 0, 0, 1))
                        list_item = OneLineAvatarIconListItem(divider='Inset')
                        list_item.height = row_height

                        lbl = MDLabel(text=str(dataframe.loc[i, c]), halign='right')


                        if i in [length - 14, length - 13, length - 12]:
                            list_item.bg_color = (.85, .30, .30, 0.5)
                            lbl.md_bg_color = (.85, .30, .30, 0.5)
                        if i == np.argmax(dataframe['rs']):
                            list_item.bg_color = (1, 0, 0, 1)
                            lbl.md_bg_color = (1, 0, 0, 1)
                        elif i == np.argmin(dataframe['rs']):
                            list_item.bg_color = (0, 1, 0, 1)
                            lbl.md_bg_color = (0, 1, 0, 1)
                        if i > 0:
                            if dataframe.loc[i, c] > 1 and dataframe.loc[i - 1, c] < 1:
                                list_item.bg_color = (.30, 1, .30, 0.5)
                                lbl.md_bg_color = (.30, 1, .30, 0.5)
                            elif dataframe.loc[i, c] < 1 and dataframe.loc[i - 1, c] > 1:
                                list_item.bg_color = (1, .30, .30, 0.5)
                                lbl.md_bg_color = (1, .30, .30, 0.5)

                            if data.loc[i, "close"] > data.loc[i-1, "close"] and data.loc[i, "rs"] < data.loc[i-1, "rs"]:
                                div_icon = IconRightWidget(icon='minus')
                                list_item.add_widget(div_icon)
                            if data.loc[i, "close"] < data.loc[i-1, "close"] and data.loc[i, "rs"] > data.loc[i-1, "rs"]:
                                div_icon = IconRightWidget(icon='plus')
                                list_item.add_widget(div_icon)
                        tmp_lbl.add_widget(lbl)
                        tmp_lbl.add_widget(list_item)
                    if c != 'rs':
                        tmp_lbl = MDLabel(text=str(dataframe.loc[i, c]))
                        tmp_lbl.halign = "center"
                        tmp_lbl.size_hint_y = None
                        tmp_lbl.height = row_height
                        tmp_lbl.line_width = 1
                        tmp_lbl.line_color = (0, 0, 0, 0.5)
                        if i in [length - 14, length - 13, length - 12]:
                            tmp_lbl.md_bg_color = (.85, .30, .30, 0.5)

                    row_data.append(tmp_lbl)
                tmp_data.append(row_data)
            # print(dataframe)
            master_table_data.append(tmp_data)
        master_table_data = list(map(lambda x: np.array(x, dtype=object).flatten(), np.array(master_table_data, dtype=object).T))
        master_table_data = np.array(master_table_data, dtype=object)
        for row in master_table_data:
            row_data = []
            for ls in row:
                for l in ls:
                    row_data.append(l)
            table_data.append(row_data)

        comp_data = []
        len_cmp_data = len(comps_daily)
        for i in range(len_cmp_data):
            row_data = []
            comp_name = comps_daily[i].loc[:, 'symbol'].unique()[0]
            row_data.append(create_label(text=comp_name, height=heading_height, md_bg_color=(.85, .80, .30, 0.8)))
            # print(comp_name)
            for _ in range(10):
                row_data.append(create_label(text=" ", height=heading_height, md_bg_color=(.85, .80, .30, 0.8)))
            comp_data.append(row_data)

            comp_data_tmp = []
            for ids, dataframe in enumerate([comps_daily[i], comps_thurs[i], comps_fri[i]]):
                if ids == 0:
                    dataframe = dataframe[['close', "pos", "neg", "rs"]]
                    data = comps_daily[i]
                elif ids == 1:
                    dataframe = dataframe[['pos', 'neg', "rs"]]
                    data = comps_thurs[i]
                elif ids == 2:
                    dataframe = dataframe[['pos', 'neg', "rs", "close"]]
                    data = comps_fri[i]
                else:
                    data = None
                cols = dataframe.columns
                length = len(dataframe)
                tmp_data_cols = []
                for num in range(length):
                    row_data = []
                    for c in cols:

                        if c == 'rs':
                            tmp_lbl = MDBoxLayout(line_color=(0, 0, 0, 1))
                            list_item = OneLineAvatarIconListItem(divider='Inset')
                            list_item.height = row_height
                            lbl = MDLabel(text=str(dataframe.loc[num, c]), halign='right')

                            # if num == np.argmax(dataframe['rs']):
                            #     list_item.bg_color = (1, 0, 0, 1)
                            #     lbl.md_bg_color = (1, 0, 0, 1)
                            # elif num == np.argmin(dataframe['rs']):
                            #     list_item.bg_color = (0, 1, 0, 1)
                            #     lbl.md_bg_color = (0, 1, 0, 1)
                            if num > 0:
                                if dataframe.loc[num, c] > 1 and dataframe.loc[num - 1, c] < 1:
                                    list_item.bg_color = (.30, 1, .30, 0.5)
                                    lbl.md_bg_color = (.30, 1, .30, 0.5)
                                elif dataframe.loc[num, c] < 1 and dataframe.loc[num - 1, c] > 1:
                                    list_item.bg_color = (1, .30, .30, 0.5)
                                    lbl.md_bg_color = (1, .30, .30, 0.5)

                                if data.loc[num, "close"] > data.loc[num - 1, "close"] and data.loc[num, 'rs'] < data.loc[num - 1, 'rs']:
                                    div_icon = IconRightWidget(icon="minus")
                                    list_item.add_widget(div_icon)
                                elif data.loc[num, "close"] < data.loc[num - 1, "close"] and data.loc[num, 'rs'] > data.loc[num - 1, 'rs']:
                                    div_icon = IconRightWidget(icon="plus")
                                    list_item.add_widget(div_icon)

                            tmp_lbl.add_widget(lbl)
                            tmp_lbl.add_widget(list_item)

                        elif c != 'rs':
                            tmp_lbl = MDLabel(text=str(dataframe.loc[num, c]))
                            tmp_lbl.halign = "center"
                            tmp_lbl.size_hint_y = None
                            tmp_lbl.height = row_height
                            tmp_lbl.line_width = 1
                            tmp_lbl.line_color = (0, 0, 0, 0.5)

                        row_data.append(tmp_lbl)
                    tmp_data_cols.append(row_data)
                comp_data_tmp.append(tmp_data_cols)
            comp_data_tmp = list(map(lambda x: np.array(x, dtype=object).flatten(), np.array(comp_data_tmp, dtype=object).T))
            comp_data_tmp = np.array(comp_data_tmp, dtype=object)
            for row in comp_data_tmp:
                row_data = []
                for ls in row:
                    for l in ls:
                        row_data.append(l)
                comp_data.append(row_data)
        return np.array(table_data, dtype=object).flatten(), np.array(comp_data, dtype=object).flatten()

    def refresh_view(self, index_data, comp_data):

        # comp_data = self.create_data()
        index_table_obj = self.ids['index_table_box']
        comp_table_obj = self.ids['comp_table_box']
        buttons_obj = self.ids['buttons_box']
        if self.table_set:
            index_table_obj.clear_widgets()
            comp_table_obj.clear_widgets()
            buttons_obj.clear_widgets()

        index_table_obj.cols = 11
        index_table_obj.rows = 16
        for lbl in index_data:
            index_table_obj.add_widget(lbl)

        comp_table_obj.cols = 11
        # print(len(comp_data))
        comp_table_obj.rows = len(comp_data) // 11

        for lbl in comp_data:
            comp_table_obj.add_widget(lbl)

        def back_to_start():
            self.manager.current = 'start'
            self.manager.transition.direction = 'right'

        back_anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        back_anchor.add_widget(
            MDRectangleFlatButton(
                text='Back',
                font_style="H5",
                on_release=lambda _: back_to_start()
            )
        )
        buttons_obj.add_widget(back_anchor)

        self.table_set = True


class mainapp(MDApp):
    def build(self):
        screen = Builder.load_file("screens.kv")
        return screen


if __name__ == '__main__':
    mainapp().run()
