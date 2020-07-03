import os
from os import path
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import pyfiglet
import openpyxl
import sqlite3
from datetime import datetime
from datetime import date
from math import ceil
import pandas as pd
import requests
from bs4 import BeautifulSoup
import math
import collections
import xlrd
import xlsxwriter
import glob






tradeIDPos = 0
typePos = 1
dateTimePos = 2
candlePricePos = 3
#
#
#
profitLossPercentLeveragePos = 7
bybitFeePos = 8
accountBalancePos = 9
tradeNetProfitPos = 10

dateFormat = "%d/%m/%Y %H:%M"





class Trade():
    def __init__(self, entryOrder, exitOrder):
        self.entry = entryOrder
        self.exit = exitOrder

        self.id = self.entry.tradeID

        self.balance = self.exit.balance
        self.date = self.exit.date
        self.profitLossPercent = self.exit.profitLossPercent





class EntryOrder():
    def __init__(self, order, fake=False):
        
        if fake == False:
            self.tradeID = order[tradeIDPos]

            self.type = "Entry"

            if "Short" in self.type:
                self.position = "Short"
            elif "Long" in self.type:
                self.position = "Long"
            else:
                self.position = "Unknown"



            self.date = order[dateTimePos]
            self.candlePrice = order[candlePricePos]

        else:
            self.tradeID = 0
            self.type = "Entry"
            self.position = "FAKE"

            dateInFront = order[dateTimePos]

            if dateInFront.month == 1:
                newMonth = 12
                newYear = dateInFront.year - 1
                newDay = 1
                newHour = dateInFront.hour
                newMinute = dateInFront.minute
            else:
                newMonth = dateInFront.month - 1
                newYear = dateInFront.year
                newDay = 1
                newHour = dateInFront.hour
                newMinute = dateInFront.minute

            dateString = f"{newDay}/{newMonth}/{newYear} {newHour}:{newMinute}"
            
            self.date = datetime.strptime(dateString, dateFormat)
            self.candlePrice = order[candlePricePos]





class ExitOrder():
    def __init__(self, order, fake=False, initialCapital=1000):

        if fake == False:

            fullType = order[typePos]

            self.type = "Exit"

            if "Short" in fullType:
                self.position = "Short"
            elif "Long" in fullType:
                self.position = "Long"
            else:
                self.position = "Unknown"
        
            self.date = order[dateTimePos]
            self.candlePrice = order[candlePricePos]
            self.profitLossPercent = order[profitLossPercentLeveragePos]
            self.bybitFee = order[bybitFeePos]
            self.balance = order[accountBalancePos]
            self.tradeNetProfit = order[tradeNetProfitPos]
        else:
            self.type = "Exit"
            self.position = "FAKE"

            dateInFront = order[dateTimePos]

            if dateInFront.month == 1:
                newMonth = 12
                newYear = dateInFront.year - 1
                newDay = 1
                newHour = dateInFront.hour
                newMinute = dateInFront.minute
            else:
                newMonth = dateInFront.month - 1
                newYear = dateInFront.year
                newDay = 1
                newHour = dateInFront.hour
                newMinute = dateInFront.minute

            dateString = f"{newDay}/{newMonth}/{newYear} {newHour}:{newMinute}"
            
            self.date = datetime.strptime(dateString, dateFormat)
            self.candlePrice = 0
            self.profitLossPercent = 0
            self.bybitFee = 0
            self.balance = initialCapital
            self.tradeNetProfit = 0





class Sheet():
    def __init__(self, sheet):
        self.trades = []
        



        # Template for Sheet AS FOLLOWS:

            # Information about the System = Column A : Row 2  == Index[0]
            # Leverage = Column I : Row 2  == Index[8]
            # INITIAL CAPITAL = Column K : Row 2  == Index[10]

            # The Trades should always start on Row 5
            
            # Trade # Number should be on = Column A  == Index[0]
            # Type should be on = Column B  == Index[1]
            # Date/Time = Column C  == Index[2]
            # Candle Price = Column D  == Index[3]
            # Profit/Loss $ = Column E  == Index[4]
            # Profit/Loss % Raw = Column F  == Index[5]
            # Profit/Loss % Fixed = Column G  == Index[6]
            # Profit/Loss % with Leverage = Column H  == Index[7]
            # Bybit Fee $ = Column I  == Index[8]
            # Post Trade Account Balance $ = Column J  == Index[9]
            # Trade Net Profit = Column K  == Index[10]



        rows = sheet.values.tolist()

        sheetSettingsRow = rows[0]
        infoPos = 0
        leveragePos = 8
        initialCapitalPos = 10


        tradeStartRow = 3


        self.info = sheetSettingsRow[infoPos]
        self.leverage = sheetSettingsRow[leveragePos]
        self.initialCapital = sheetSettingsRow[initialCapitalPos]


        firstEntry = rows[tradeStartRow]
        firstExit = rows[tradeStartRow + 1]

        fakeEntry = EntryOrder(firstEntry, fake=True)
        fakeExit = ExitOrder(firstExit, fake=True, initialCapital=self.initialCapital)

        self.fakeTrade = Trade(fakeEntry, fakeExit)

        unParsedEntriesExits = []

        

        for rowIndex in range(tradeStartRow, len(rows)):
            if "Entry" in str(rows[rowIndex][typePos]):
                entryOrder = EntryOrder(rows[rowIndex])
                unParsedEntriesExits.append(entryOrder)
            elif "Exit" in str(rows[rowIndex][typePos]):
                exitOrder = ExitOrder(rows[rowIndex])
                unParsedEntriesExits.append(exitOrder)
            else:
                continue
        

        tupleEntryExits = iter(unParsedEntriesExits)

        for x in tupleEntryExits:
            newTrade = Trade(x, next(tupleEntryExits))
            self.trades.append(newTrade)
        

        for eachTrade in self.trades:
            print(eachTrade.balance)
            print(eachTrade.date)
        

        print("\n\n")
        print(self.fakeTrade.balance)





class Spreadsheet():
    def __init__(self, path):
        self.sheets = []
        pd.set_option('display.max_rows', None)

        xl = pd.ExcelFile(path)
        # print(f"{path} could not converted to Spreadsheet object.")
        

        self.dfs = {sheet: xl.parse(sheet).fillna(0) for sheet in xl.sheet_names}

        # ['BTC 136 Min - Key 4 - ATR 3- Smooth 6- DI Length 15 -ADX Filter 25- -Range 1.2/1.7-look 2 - TP 28.5/37- SL 0.5/2- TSL 1.5/7.6 - do buy 3 mill/-13 mill don’t buy 44.5 mill/-44.5 mill - 2.2/3.1', 0, 0, 'Fixed TP:', 0, 'Stop Loss:', 0, 'Leverage Setting:', 2.25, 'Initial Capital:', 1000]
        # ['Trade #', 'Type', 'Date/Time', 'Candle Price', 'Profit/Loss $', 'Profit/Loss % Raw', 'Profit/Loss % Fixed', 'Profit/Loss % with Leverage', 'Bybit Fee $', 'Post Trade Account Balance $', 'Trade Net Profit']


        for eachSheet in self.dfs:
            sheet = Sheet(self.dfs[eachSheet])
            self.sheets.append(sheet)





class Backtest():
    def __init__(self, path):
        self.spreadsheets = []

        isDirectory = os.path.isdir(path)

        if isDirectory == False:
            raise Exception("Directory not found. Please make sure path is leading to a folder, and not to the file itself.")


        allFiles = os.listdir(path)
        if '.DS_Store' in allFiles:
            allFiles.remove('.DS_Store')

        if len(allFiles) == 0:
            raise Exception("Directory Found, but no files are in directory.")


        spreadsheetFileNames = []
        for eachFile in glob.glob(f"{path}/*.xlsx"):
            spreadsheetFileNames.append(eachFile)

        if len(spreadsheetFileNames) == 0:
            raise Exception("Files in directory are not in an XLSX format.")

        print(spreadsheetFileNames)

        for eachSpreadsheet in spreadsheetFileNames:
            spreadsheetObject = Spreadsheet(eachSpreadsheet)
            self.spreadsheets.append(spreadsheetObject)

































def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/Imports"

    backtest = Backtest(path)
    





if __name__ == "__main__":
    main()