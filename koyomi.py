import requests
import configs
from bs4 import BeautifulSoup
import datetime

class Koyomi:

    def __init__(self):
        self.__data = []
        self.__mode = 0  # 0：メニュー選択状態 , 1：メニュー１選択時 , ２：メニュー２選択時

        r = requests.get(configs.SCRAPING_URL)         
        soup = BeautifulSoup(r.content, "html.parser")
        tr_all = soup.find_all("tr")
        for tr in tr_all:
            if tr.th.text != configs.WAREKI and tr.th.text != configs.SEIREKI:
                self.__data.append(
                    {
                        'wareki': tr.th.text,
                        'seireki': tr.td.text
                    }
                )

    def get_content(self, msg):
        #どれにもマッチしないメッセージはメニューを開く為デフォルトで指定
        content = self.menu()
        if msg == configs.MENU:
            self.__mode = 0
        else:
            if self.__mode == 0:
                if msg == '1' or msg == '１':
                    self.__mode = 1
                    content = self.nav_seireki_toggle_wareki()
                elif msg == '2' or msg == '２':
                    self.__mode = 2
                    content = self.nav_reiwa_toggle_heisei()
                elif msg == '3' or msg == '３':
                    content = self.now_info()
            elif self.__mode == 1:
                content = configs.ERROR_MESSAGE
                if msg[-1:] == configs.NEN:
                    if (configs.REIWA in msg) or (configs.HEISEI in msg):
                        content = self.wareki_to_seireki(msg)
                    elif len(msg) == 5:
                        content = self.seireki_to_wareki(msg)
            elif self.__mode == 2:
                content = configs.ERROR_MESSAGE
                if msg[-1:] == configs.NEN:
                    if configs.REIWA in msg:
                        content = self.reiwa_to_heisei(msg)
                    elif configs.HEISEI in msg:
                        content = self.heisei_to_reiwa(msg)
            else:
                self.__mode = 0

        return content


    def menu(self):
        return configs.MENU_MESSAGE
    
    def nav_seireki_toggle_wareki(self):
        return configs.NAV_SEIREKI_TOGGLE_WAREKI_MESSAGE
    
    def nav_reiwa_toggle_heisei(self):
        return configs.NAV_REIWA_TOGGLE_HEISEI_MESSAGE

    def seireki_to_wareki(self, msg):
        r = configs.NONE_DATA_WAREKI
        for d in self.__data:
            if d['seireki'] in msg:
                r = '''{0}は、
{1}です☀️'''.format(msg, d['wareki'])
        return r
    def wareki_to_seireki(self, msg):
        r = configs.NONE_DATA_SEIREKI
        for d in self.__data:
            if d['wareki'] in msg:
                r = '''{0}は、
{1}年です☀️'''.format(msg, d['seireki'])
        return r
    def seireki_to_wareki_simple(self, msg):
        r = ''
        for d in self.__data:
            if d['seireki'] in msg:
                r = d['wareki']
        return r      
    
    def reiwa_to_heisei(self, msg):
        s = msg[2:]
        if configs.NEN in s:
            s = s[:-1]
        year = int(s) + configs.REIWA_TOGGLE_HEISEI_NUM
        return '''{0}は、
{1}です✨'''.format(msg, configs.HEISEI + str(year) + configs.NEN)
    
    def heisei_to_reiwa(self, msg):
        s = msg[2:]
        if configs.NEN in s:
            s = s[:-1]
        year = int(s) - configs.REIWA_TOGGLE_HEISEI_NUM     
        return '''{0}は、
{1}です✨'''.format(msg, configs.REIWA + str(year) + configs.NEN)

    def now_info(self):
        now_date = datetime.datetime.now()
        y = str(now_date.year) + configs.NEN
        m = str(now_date.month) + configs.TUKI
        d = str(now_date.day) + configs.NITI
        wareki = self.seireki_to_wareki_simple(y)

        dt1 = datetime.datetime(2019, 5, 1, 0, 00, 00)
        dt2 = datetime.datetime(now_date.year, now_date.month, now_date.day, now_date.hour, now_date.minute, now_date.second)
        df = dt2 - dt1

        return '''今日は、
{0}({1}) {2}です。
令和が始まってから、{3}秒が経過しました🔔
'''.format(y, wareki, m + d, df.seconds)
