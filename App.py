import pandas as pd
import numpy as np
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from kivymd.uix.picker import MDDatePicker
from kivy.core.window import Window
from plyer import filechooser
from utils import *
import datetime
import json

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
                if type(sym) == tuple:
                    fp.write(f"\t\t{i + 1}. {sym[0]} - {sym[1]}\n")
                elif type(sym) == str:
                    fp.write(f"\t\t{i + 1}. {sym}\n")

    def daily_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        INSUF_DATA = set()
        for name, frame in data:
            frame = frame[::-1].reset_index(drop=True)
            try:
                close = np.array(frame.loc[:, "CLOSE"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = np.sum(pos_1) / np.sum(neg_1)
                rs_2 = np.sum(pos_2) / np.sum(neg_2)
                if rs_1 <= 0.3:
                    RS_LS0P3.append((name, rs_1))
                if rs_1 < 1 and rs_2 > 1:
                    RS_HIGH_TO_LS1.append((name, rs_1))
                if rs_1 > 1 and rs_2 < 1:
                    RS_LS_TO_GR1.append((name, rs_1))
            except IndexError as e:
                INSUF_DATA.add(name)
                # print(f"{e} Encountered. Halting procedure")

        return {"ls0.3": RS_LS0P3, "ls2gr1": RS_LS_TO_GR1, "gr2ls1": RS_HIGH_TO_LS1, "insuf": INSUF_DATA}

    def thurs_weekly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        INSUF_DATA = set()
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "DATE"]
            final_data = []
            count = 16
            while count > 0:
                try:
                    if date.strftime("%A") != "Thursday":
                        date -= timedelta(days=1)
                    else:
                        trading_date = previousTradingDay(date)
                        d = frame[frame['DATE'] == trading_date.strftime("%Y/%m/%d")].values
                        # print(d)
                        final_data.append(d[0])
                        date -= timedelta(days=7)
                        count -= 1
                except IndexError as e:
                    INSUF_DATA.add(name)
                    # print(f"{e} Encountered. Halting procedure")
                    count -= 1
            if len(final_data) >= 16:
                final_data = pd.DataFrame(final_data, columns=frame.columns)

                close = np.array(final_data.loc[:, "CLOSE"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = np.sum(pos_1) / np.sum(neg_1)
                rs_2 = np.sum(pos_2) / np.sum(neg_2)
                roc_1 = close[0] / close[13]
                roc_2 = close[1] / close[14]

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

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "ls2gr1roc": ROC_LS_TO_GR1,
                "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA}

    def friday_weekly_batch_report(self, data):
        RS_LS0P3 = []
        RS_HIGH_TO_LS1 = []
        RS_LS_TO_GR1 = []
        ROC_LS_TO_GR1 = []
        ROC_HIGH_TO_LS1 = []
        INSUF_DATA = set()
        for name, frame in data:
            # print(name)
            frame = frame[::-1].reset_index(drop=True)
            date = frame.loc[0, "DATE"]
            final_data = []
            count = 16
            while count > 0:
                try:
                    if date.strftime("%A") != "Friday":
                        date -= timedelta(days=1)
                    else:
                        trading_date = previousTradingDay(date)
                        d = frame[frame['DATE'] == trading_date.strftime("%Y/%m/%d")].values
                        # print(d)
                        final_data.append(d[0])
                        date -= timedelta(days=7)
                        count -= 1
                except IndexError as e:
                    INSUF_DATA.add(name)
                    # print(f"{e} Encountered. Halting procedure")
                    count -= 1
            if len(final_data) >= 16:
                final_data = pd.DataFrame(final_data, columns=frame.columns)

                close = np.array(final_data.loc[:, "CLOSE"])
                pos_1 = [max(0, x) for x in (close[:14] - close[1:15])]
                pos_2 = [max(0, x) for x in (close[1:15] - close[2:16])]
                neg_1 = [-min(0, x) for x in (close[:14] - close[1:15])]
                neg_2 = [-min(0, x) for x in (close[1:15] - close[2:16])]
                rs_1 = np.sum(pos_1) / np.sum(neg_1)
                rs_2 = np.sum(pos_2) / np.sum(neg_2)
                roc_1 = close[0] / close[13]
                roc_2 = close[1] / close[14]

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

        return {"ls0.3": RS_LS0P3, "ls2gr1rs": RS_LS_TO_GR1, "gr2ls1rs": RS_HIGH_TO_LS1, "ls2gr1roc": ROC_LS_TO_GR1,
                "gr2ls1roc": ROC_HIGH_TO_LS1, "insuf": INSUF_DATA}

    def get_batch_report(self):
        cur = sqlite3.connect(dbpath).cursor()
        columns = ["SYMBOL", "DATE", "CLOSE"]
        data = pd.DataFrame(cur.execute("SELECT * FROM stocks"), columns=columns)
        data['DATE'] = data['DATE'].apply(lambda x: datetime.datetime.strptime(x, "%Y/%m/%d"))
        data = data.groupby("SYMBOL")
        if not os.path.exists(report_dir_path):
            os.mkdir(report_dir_path)
        filename = rf"BatchReport - {datetime.datetime.today().date().strftime('%Y-%m-%d')}.txt"

        daily_lists = self.daily_batch_report(data)
        thursday_lists = self.thurs_weekly_batch_report(data)
        friday_lists = self.friday_weekly_batch_report(data)

        filepath = os.path.join(report_dir_path, filename)
        try:
            fp = open(filepath, "w")
            fp.write(
                f"*** Batch Report for the 526 Symbols - {datetime.datetime.today().date().strftime('%Y/%m/%d')}***\n")
            fp.write(f"\nDAILY RS")
            self.log(fp=fp, title="CATEGORY: RS < 0.3", list=daily_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Present RS > 1, Past RS < 1", list=daily_lists['ls2gr1'])
            self.log(fp=fp, title="CATEGORY: Present RS < 1, Past RS > 1", list=daily_lists['gr2ls1'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=daily_lists['insuf'])
            fp.write(f"\nWEEKLY - THURSDAY RS")
            self.log(fp=fp, title="CATEGORY: RS < 0.3", list=thursday_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Present RS > 1, Past RS < 1", list=thursday_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Present RS < 1, Past RS > 1", list=thursday_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Present ROC > 1, Past ROC < 1", list=thursday_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Present ROC < 1, Past ROC > 1", list=thursday_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=thursday_lists['insuf'])
            fp.write(f"\nWEEKLY - FRIDAY RS")
            self.log(fp=fp, title="CATEGORY: RS < 0.3", list=friday_lists['ls0.3'])
            self.log(fp=fp, title="CATEGORY: Present RS > 1, Past RS < 1", list=friday_lists['ls2gr1rs'])
            self.log(fp=fp, title="CATEGORY: Present RS < 1, Past RS > 1", list=friday_lists['gr2ls1rs'])
            self.log(fp=fp, title="CATEGORY: Present ROC > 1, Past ROC < 1", list=friday_lists['ls2gr1roc'])
            self.log(fp=fp, title="CATEGORY: Present ROC < 1, Past ROC > 1", list=friday_lists['gr2ls1roc'])
            self.log(fp=fp, title="CATEGORY: Insufficient Data", list=friday_lists['insuf'])
            fp.close()
            print("Batch Report creation successful")
            return True
        except Exception as e:
            print(e)
            print("Batch Report creation unsuccessful")
            return False


class MaintainScreen(Screen):

    def updateDb(self, dbpath):
        dbconn = sqlite3.connect(dbpath)
        lastday = lastTradingDay(dbpath)
        while lastday < previousTradingDay(datetime.datetime.today().date()):
            lastday += timedelta(days=1)
            # print(lastday)
            if lastday.strftime("%Y-%m-%d") not in nse_holidays:
                filepath = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + bhavfilename)
                csvfile = os.path.join(datapath, lastday.strftime("%Y-%m-%d") + ".csv")

                try:
                    os.rename(filepath, csvfile)
                except FileNotFoundError:
                    print(f"File {filepath} not found")

                data = pd.read_csv(csvfile, delimiter=",",
                                   names=["symbol", "date", "open", "high", "low", "close", "volume", "openI"])[
                    ["symbol", "date", "close"]]
                data['date'] = data['date'].apply(lambda x: f"{str(x)[:4]}/{str(x)[4:6]}/{str(x)[6:8]}")
                data = data[data['symbol'].isin(symbols)]
                try:
                    data.to_sql(name="stocks", con=dbconn, if_exists="append", index=False)
                except sqlite3.IntegrityError as e:
                    print(f"{e} occured")

    def updateSymbols(self):
        file = filechooser.open_file()
        print(file)

    def updateHolidays(self):
        file = filechooser.open_file()
        print(file)


class InputScreen(Screen):
    def expand(self):
        self.symbols = symbols
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "currency-inr",
                "text": sym,
                "height": dp(56),
                "on_release": lambda x=sym: self.set_item(x, "drop_item"),
            } for sym in self.symbols
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids['drop_item'],
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.menu.bind()
        self.menu.open()

    def set_item(self, text_item, id):
        self.ids[id].text = text_item
        self.menu.dismiss()

    def on_save(self, instance, value, date_range):
        self.ids['start_date_input'].text = str(value)
        self.ids['start_date_input'].error = False
        self.ids['start_date_input'].helper_text = "Valid Date"

    def date_picker(self):
        todate = last14Tradingdays(min(datetime.datetime.today().date(), lastTradingDay(dbpath)))
        date_dialog = MDDatePicker(year=todate.year, month=todate.month, day=todate.day)
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def tp_expand(self):
        symbols = ["Daily", "Weekly - Monday", "Weekly - Tuesday", "Weekly - Wednesday", "Weekly - Thursday",
                   "Weekly - Friday"]
        menu_items = [
            {
                "viewclass": "IconListItem",
                "icon": "timer",
                "text": sym,
                "height": dp(56),
                "on_release": lambda x=sym: self.set_item(x, "tp_drop"),
            } for sym in symbols
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
        startdate = datetime.datetime.strptime(self.ids['start_date_input'].text, "%Y-%m-%d").date()
        timeperiod = self.ids['tp_drop'].text.split(" - ")[-1]
        cur = sqlite3.connect(dbpath).cursor()
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

        if timeperiod == "Daily":
            rqd_data = last14Tradingdays(min(datetime.datetime.today().date(), lastTradingDay(dbpath)))
            if startdate <= rqd_data:
                # print("Valid - Daily")
                self.build()
                return True
            # print("Invalid - Daily")
            popup = MDDialog(
                title="Insufficient Data Points",
                text=f"Select a date before {rqd_data}",
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
        elif timeperiod != "Time Period":
            rqd_date = last14daysWeekly(lastTradingDay(dbpath), timeperiod)
            if startdate <= rqd_date:
                # print("Valid - Weekly")
                self.build()
                return True
            # print("Invalid - Weekly")
            popup = MDDialog(
                title="Insufficient Data Points",
                text=f"Select a date before {rqd_date}",
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
        elif timeperiod == "Time Period":
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

    def get_data(self, settings):
        db_conn = sqlite3.connect(database=dbpath)
        cur = db_conn.cursor()
        columns = list(map(lambda x: x[0].upper(), cur.execute(columns_query)))
        data = pd.DataFrame(cur.execute("SELECT * FROM stocks WHERE symbol=:sym", {"sym": settings['symbol']}),
                            columns=columns).loc[:, ("DATE", "CLOSE")][::-1]
        data["DATE"] = data["DATE"].apply(datetime.datetime.strptime, args=("%Y/%m/%d",))
        data["DATE"] = data["DATE"].apply(lambda x: x.date())

        startdate = datetime.datetime.strptime(settings['startdate'], "%Y-%m-%d").date()

        if settings['timeperiod'] == "Daily":
            data = data[(data["DATE"] >= startdate)][::-1].reset_index(drop=True)
            final_data = self.process(data, settings)
            return final_data
        elif settings['timeperiod'] != "Time Period":
            day = settings['timeperiod'].split(" - ")[-1]
            data = data[(data["DATE"] >= startdate)][::-1].reset_index(drop=True)
            dates = []

            while (startdate <= lastTradingDay(dbpath)):
                if startdate.strftime("%A") == day:
                    prev_date = previousTradingDay(startdate).strftime("%Y/%m/%d")
                    dates.append(prev_date)
                    startdate += timedelta(days=7)
                else:
                    startdate += timedelta(days=1)

            for i in range(len(data)):
                if data.loc[i, "DATE"].strftime("%Y/%m/%d") not in dates:
                    data = data.drop(i)
            data = data.reset_index(drop=True)
            final_data = self.process(data, settings)
            return final_data

    def process(self, data, settings):
        n = len(data)
        data["POS"] = np.zeros(n)
        data["NEG"] = np.zeros(n)
        data["LAST n POS"] = np.zeros(n)
        data["LAST n NEG"] = np.zeros(n)
        data["RS"] = np.zeros(n)
        data["ROC"] = np.zeros(n)

        for i in range(1, n):
            data.loc[i, "POS"] = round(max(0, data.loc[i, "CLOSE"] - data.loc[i - 1, "CLOSE"]), 2)
            data.loc[i, "NEG"] = -round(min(0, data.loc[i, "CLOSE"] - data.loc[i - 1, "CLOSE"]), 2)

        data = data[::-1].reset_index(drop=True)

        for i in range(0, n - settings['frequency']):
            data.loc[i, 'LAST n POS'] = round(np.sum(data.loc[i: i + settings['frequency'] - 1, "POS"]), 2)
            data.loc[i, 'LAST n NEG'] = round(np.sum(data.loc[i: i + settings['frequency'] - 1, "NEG"]), 2)
            data.loc[i, "ROC"] = round(data.loc[i, "CLOSE"] / data.loc[i + 13, "CLOSE"], 2)
            data.loc[i, "RS"] = round(data.loc[i, "LAST n POS"] / data.loc[i, "LAST n NEG"], 2)
        data = data[::-1].reset_index(drop=True)

        return data

    def build(self):
        symbol = self.ids['drop_item'].text
        startdate = self.ids['start_date_input'].text
        timeperiod = self.ids["tp_drop"].text
        frequency = int(self.ids['frequency_input'].text)

        settings = {"symbol": symbol, "startdate": startdate, "timeperiod": timeperiod, "frequency": frequency}
        json_obj = json.dumps(
            settings, indent=4)
        with open("settings.json", "w") as fp:
            fp.write(json_obj)

        stock_data = self.get_data(settings)
        dates = stock_data["DATE"].to_list()
        cols = stock_data.columns
        print(dates)

        table_data = []
        for c in cols:
            table_data.append(
                {'text': c, 'size_hint_y': None, 'height': 30, "line_width": (0, 0, 0, 1), "halign": "center",
                 'md_bg_color': (.85, .80, .30, 1)})  # append the data

        for z in range(len(dates)):
            for y in cols:
                label_dict = {'text': str(stock_data.loc[z, y]), "line_color": (0, 0, 0, 1), "halign": "center",
                              'size_hint_y': None, 'height': 20}
                if y == "RS" and z > 0:
                    if stock_data.loc[z, "RS"] > 1 and stock_data.loc[z - 1, "RS"] < 1:
                        label_dict['md_bg_color'] = (0, 1, 0, 0.75)
                    if stock_data.loc[z, "RS"] < 1 and stock_data.loc[z - 1, "RS"] > 1:
                        label_dict['md_bg_color'] = (1, 0, 0, 0.75)
                table_data.append(label_dict)  # append the data

        print(table_data)
        self.ids['table_floor_layout'].cols = len(cols)
        self.ids['table_floor'].data = table_data


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


class mainapp(MDApp):
    def build(self):
        screen = Builder.load_file("screens.kv")
        return screen


if __name__ == '__main__':
    mainapp().run()
