import time
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
import sys
import os
import csv
import threading

from lib import api

class DemoTrade(QMainWindow):
    
    def msg_internet(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("No Internet Connection!\nPlease try again.")
        msg.setStandardButtons(QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Close)
        msg.setIcon(QMessageBox.Icon.Warning)
        result = msg.exec_()
        if result ==  QMessageBox.StandardButton.Retry:
            self.__init__()
        else:
            sys.exit()
  
    def check_dir(self):
        if not os.path.isdir('logs/'):
            os.makedirs('logs')
      
    def get_market_list(self):
        self.markets = self.robot.get_list()
        if self.markets != 0:
            coin = []
            for key in self.markets.keys():
                coin.append(self.markets[key])
            self.marketbox.addItems(coin)
        else:
            self.msg_internet()
                
    def __init__(self):
        super(DemoTrade, self).__init__()
        uic.loadUi('ui/main.ui', self)
        self.robot = api.API()
        self.check_dir()
        self.__open_position = False
        self.__pos = None
        self.marketbox.currentIndexChanged.connect(self.select_market)
        self.marketbox.setEditable(True)
        self.closebutton.clicked.connect(self.close_button)
        self.closebutton.setEnabled(False)
        self.openbutton.clicked.connect(self.open_button)
        self.clearbutton.clicked.connect(self.clear_button)
        self.aboutmebutton.clicked.connect(self.about_me)
        self.tpslsub.clicked.connect(self.tpsl_submit)
        self.get_market_list()
        self.timer = threading.Timer(0.5, lambda: self.update()).start()
        self.show()
    
    def check_file(self, file_name):
        if not os.path.isfile(file_name):
            open(file_name, 'w').close()
        if os.path.getsize(file_name) == 0:
            with open(file_name, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['Market', 'Time', 'Position', 'Buy Price', 'Sell Price', 'TP', 'SL', 'Leverage', 'Percent', 'Balance'])
    
    def check_open_position(self, file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            last_line = lines[-1].rstrip('\n')
            results = last_line.split(',')
            # [Market,Time, Position, Buy Price, Sell Price, TP, SL, Leverage, Percent, Balance]
            if results[0] != 'Market':
                if results[8] == 'nan':
                    self._start_time = results[1]
                    self._pos = results[2]
                    if self._pos == 'LONG':
                        self._buy_price = float(results[3])
                    else:
                        self._sell_price = float(results[4])
                    self._tp = results[5]
                    self._sl = results[6]
                    if self._tp != 'nan':
                        self.tp_edit.setText(self._tp)
                        self.sl_edit.setText(self._sl)
                        self._tp = float(self._tp)
                        self._sl = float(self._sl)
                    self._leverage = int(results[7])
                    self.leveragebox.setCurrentText(str(self._leverage))
                    self._percent = results[8]
                    balance = lines[-2].rstrip('\n').split(',')[-1]
                    if balance == 'Balance':
                        self._balance = 100.0
                        self.cost_label.setText(str(100.0))
                    else:
                        self._balance = float(balance)
                        self.cost_label.setText(str(self._balance))
                    self.cost_label.setText(str(self._balance))
                    self.__open_position = True
                    self.closebutton.setEnabled(True)
                    self.openbutton.setEnabled(False)
                    self.clearbutton.setEnabled(False)
                else:
                    self._balance = float(results[9])
                    self.cost_label.setText(str(self._balance))
                    self.__open_position = False
            else:
                self._balance = 100.0
                self.cost_label.setText(str(self._balance))
                self.__open_position = False
        
    def select_market(self):
        self.reset()
        self._market = self.marketbox.currentText()
        self._id = list(self.markets.keys())[list(self.markets.values()).index(self._market)]
        self.coin_price_label.setText(str(self.robot.get_kline(self._id)))
        file_name = 'logs/{market}.csv'.format(market=self._market)
        self.check_file(file_name)
        self.check_open_position(file_name)
        
    def close_button(self):
        msg = QMessageBox()
        msg.setWindowTitle("Close Position")
        msg.setText("Are you sure you want to do this?")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Warning)
        result = msg.exec_()
        if result ==  QMessageBox.StandardButton.Ok:
            self.close_pos()
    
    def open_button(self):
        msg = QMessageBox()
        msg.setWindowTitle("Open Position")
        msg.setText("Are you sure you want to do this?")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Warning)
        result = msg.exec_()
        if result ==  QMessageBox.StandardButton.Ok:
            price = float(self.robot.get_kline(self._id))
            self.__open_position = True
            self._tp = 'nan'
            self._sl = 'nan'
            if self.pos_long.isChecked():
                self._pos = 'LONG'
                self._buy_price = price
                self._leverage = int(self.leveragebox.currentText())
                self._start_time = time.time()
                file_name = 'logs/{market}.csv'.format(market=self._market)
                with open(file_name, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([self._market, self._start_time, self._pos, str(self._buy_price), 'nan', 'nan', 'nan', str(self._leverage), 'nan', str(self._balance)])
            if self.pos_short.isChecked():
                self._pos = 'SHORT'
                self._sell_price = price
                self._leverage = int(self.leveragebox.currentText())
                self._start_time = time.time()
                file_name = 'logs/{market}.csv'.format(market=self._market)
                with open(file_name, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([self._market, self._start_time, self._pos, 'nan', str(self._sell_price), 'nan', 'nan', str(self._leverage), 'nan', str(self._balance)])
            self.openbutton.setEnabled(False)
            self.closebutton.setEnabled(True)
            self.clearbutton.setEnabled(False)
    
    def clear_button(self):
        msg = QMessageBox()
        msg.setWindowTitle("Clear History")
        msg.setText("Are you sure you want to do this?\nInformation is not reversible.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setIcon(QMessageBox.Icon.Warning)
        result = msg.exec_()
        if result ==  QMessageBox.StandardButton.Ok:
            file_name = 'logs/{market}.csv'.format(market=self._market)
            open(file_name, 'w').close()
            with open(file_name, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(['Market', 'Time', 'Position', 'Buy Price', 'Sell Price', 'TP', 'SL', 'Leverage', 'Percent', 'Balance'])
    
    def tpsl_submit(self):
        tp = self.tp_edit.text()
        sl = self.sl_edit.text()
        if tp == '' or sl == '':
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("You must set both sl/tp.")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec_()
        else:
            self._tp = float(tp)
            self._sl = float(sl)
            #remove last line
            file_name = 'logs/{market}.csv'.format(market=self._market)
            f = open(file_name)
            lines = f.readlines()
            f.close()
            w = open(file_name, 'w')
            w.writelines([item for item in lines[:-1]])
            w.close()
            with open(file_name, 'a') as f:
                writer = csv.writer(f)
                if self._pos == 'LONG':
                    writer.writerow([self._market, self._start_time, self._pos, str(self._buy_price), 'nan', str(self._tp), str(self._sl), str(self._leverage), 'nan', str(self._balance)])
                else:
                    writer.writerow([self._market, self._start_time, self._pos, 'nan', str(self._sell_price), str(self._tp), str(self._sl), str(self._leverage), 'nan', str(self._balance)])
    
    def about_me(self):
        msg = QMessageBox()
        msg.setWindowTitle("About Me")
        msg.setTextFormat(QtCore.Qt.TextFormat.RichText)
        msg.setText("Hi. I am Qasem Talaee.<br>"
                    "I am a computer programmer and I do trade.<br>"
                    "I wrote this software for free, hoping that you will be successful.<br>"
                    "<b><i>Enjoy It My Friend !</i></b><br><br>"
                    "My Github : <a href='https://github.com/qasem-talaee'>https://github.com/qasem-talaee</a><br>"
                    "My Website : <a href='http://qtle.ir'>http://qtle.ir</a><br>"
                    "My Email : <a href='mailto:qasem.talaee1375@gmail.com'>qasem.talaee1375@gmail.com</a><br>")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec_()
    
    def close_pos(self, in_price = None):
        self.__open_position = False
        self.openbutton.setEnabled(True)
        self.closebutton.setEnabled(False)
        self.clearbutton.setEnabled(True)
        file_name = 'logs/{market}.csv'.format(market=self._market)
        #remove last line
        f = open(file_name)
        lines = f.readlines()
        f.close()
        w = open(file_name, 'w')
        w.writelines([item for item in lines[:-1]])
        w.close()
        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            if self._pos == 'LONG':
                price = in_price or float(self.robot.get_kline(self._id))
                percent = ((price - self._buy_price) / (price)) * 100 * self._leverage
                balance = (percent / 100) * self._balance + self._balance
                writer.writerow([self._market, self._start_time, self._pos, str(self._buy_price), str(price), str(self._tp), str(self._sl), str(self._leverage), str(percent), str(balance)])
                self.reset()
            else:
                price = float(self.robot.get_kline(self._id))
                percent = ((self._sell_price - price) / (self._sell_price)) * 100 * self._leverage
                balance = (percent / 100) * self._balance + self._balance
                writer.writerow([self._market, self._start_time, self._pos, str(price), str(self._sell_price), str(self._tp), str(self._sl), str(self._leverage), str(percent), str(balance)])
                self.reset()
        self.cost_label.setText(str(balance))
    
    def reset(self):
        #self._buy_price = 'nan'
        #self._sell_price = 'nan'
        #self._tp = 'nan'
        #self._sl = 'nan'
        self.entry_price_label.setText('')
        self.lig_price_label.setText('')
        self.percent_label.setText('')
        self.amount_label.setText('')
        self.balance_label.setText('')
        self.leverage_label.setText('')
        self.pos_label.setText('')
        self.tp_edit.setText('')
        self.sl_edit.setText('')
    
    def update(self):
        self.coin_price_label.setText(str(self.robot.get_kline(self._id)))
        if self.__open_position:
            if self._pos == 'LONG':
                self.pos_label.setText('LONG / BUY')
                self.entry_price_label.setText(str(self._buy_price))
                self.leverage_label.setText(str(self._leverage))
                self._lig_price = (100 * self._buy_price * self._leverage) / (100 * self._leverage + 100)
                self.lig_price_label.setText(str(self._lig_price))
                price = float(self.robot.get_kline(self._id))
                percent = ((price - self._buy_price) / (price)) * 100 * self._leverage
                self.percent_label.setText(str(percent))
                amount_tpsl = (percent / 100) * self._balance
                self.amount_label.setText(str(amount_tpsl))
                amount_tpsl_balance = ((percent / 100) * self._balance) + self._balance
                self.balance_label.setText(str(amount_tpsl_balance))
                prices = self.robot.historical(self._id, self._start_time)
                if type(self._tp) == float and len(prices) != 0:
                    if max(prices) >= self._tp:
                        self.close_pos(self._tp)
                    if min(prices) <= self._sl:
                        self.close_pos(self._sl)
                if len(prices) != 0:
                    if min(prices) <= self._lig_price:
                        self.close_pos(self._lig_price)
            else:
                self.pos_label.setText('SHORT / SELL')
                self.entry_price_label.setText(str(self._sell_price))
                self.leverage_label.setText(str(self._leverage))
                self._lig_price = (self._sell_price * (100 * self._leverage + 100)) / (100 * self._leverage)
                self.lig_price_label.setText(str(self._lig_price))
                price = float(self.robot.get_kline(self._id))
                percent = ((self._sell_price - price) / (self._sell_price)) * 100 * self._leverage
                self.percent_label.setText(str(percent))
                amount_tpsl = (percent / 100) * self._balance
                self.amount_label.setText(str(amount_tpsl))
                amount_tpsl_balance = ((percent / 100) * self._balance) + self._balance
                self.balance_label.setText(str(amount_tpsl_balance))
                prices = self.robot.historical(self._id, self._start_time)
                if type(self._tp) == float and len(prices) != 0:
                    if min(prices) <= self._tp:
                        self.close_pos(self._tp)
                    if max(prices) >= self._sl:
                         self.close_pos(self._sl)
                if len(prices) != 0:
                    if max(prices) >= self._lig_price:
                        self.close_pos(self._lig_price)
        self.timer = threading.Timer(3.0, lambda: self.update()).start()

        
app = QApplication(sys.argv)
window = DemoTrade()
app.exec_()