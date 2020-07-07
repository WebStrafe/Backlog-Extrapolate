import os
from os import path
import time
import openpyxl
from datetime import datetime
from datetime import date
import pandas as pd
import requests
import math
import collections
import xlrd
import xlsxwriter
import glob
from extrapolate import Monthly_Profit
from extrapolate import Calculate_Drawdowns
from extrapolate import Highest_Drawdown
from extrapolate import Count_Periods_Drawdown
from extrapolate import Filter_Drawdowns
from extrapolate import Longest_Drawdown_Period
from extrapolate import Average_Drawdown_Period
from extrapolate import Max_Consecutive_Losses
from extrapolate import Average_Win
from extrapolate import Highest_Win
from extrapolate import Average_Loss
from extrapolate import Total_Trades
from extrapolate import Total_Wins
from extrapolate import Total_Losses
from extrapolate import Win_Rate
from extrapolate import Total_Backtest_Period
import calendar






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


tradeStartRow = 3

dateFormat = "%d/%m/%Y %H:%M"





class Trade():
    def __init__(self, entryOrder, exitOrder, fake=False):
        if fake == False:

            self.entry = entryOrder
            self.exit = exitOrder

            self.id = self.entry.tradeID

            self.balance = round(self.exit.balance, 2)
            self.date = self.exit.date
            self.profitLossPercent = self.exit.profitLossPercent

            self.month = calendar.month_name[self.date.month]
            self.year = self.date.year
            self.monthDigit = self.date.month
        else:
            self.balance = exitOrder[0]
            self.date = exitOrder[1]
            self.month = calendar.month_name[self.date.month]
            self.year = self.date.year
            self.monthDigit = self.date.month
    
    def Date(self, newDate):
        self.date = newDate
        self.month = newDate.strftime("%B")
        self.year = newDate.year
        self.monthDigit = newDate.month

        





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
    def __init__(self, sheet, id):
        self.id = str(id)
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
        

        # for eachTrade in self.trades:
        #     print(eachTrade.balance)
        #     print(eachTrade.date)
        

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


        for index, eachSheet in enumerate(self.dfs, start=0):

            rowValues = self.dfs[eachSheet].values.tolist()


            comparisonRow = ['Trade #', 'Type', 'Date/Time', 'Candle Price', 'NONE', 'NONE', 'NONE', 'Profit/Loss % with Leverage', 'Bybit Fee $', 'Post Trade Account Balance $', 'Trade Net Profit']
            comparisonIndexRow = [tradeIDPos, typePos, dateTimePos, candlePricePos, profitLossPercentLeveragePos, bybitFeePos, accountBalancePos, tradeNetProfitPos]

            checkRow = rowValues[2]
            checkFirstTradeRow = rowValues[tradeStartRow]

            print(checkFirstTradeRow)



            verified = True

            try:

                # for index, eachComparisonString in enumerate(checkRow, start=0):
                #     if index == 4 or index == 5 or index == 6:
                #         continue
                #     if index == 11:
                #         break
                #     if eachComparisonString != comparisonRow[index]:
                #         print(f"{eachComparisonString} of index {index} Out Of Place. Error!  [{eachSheet}]")
                #         verified = False


                if len(checkRow) < 11:
                    verified = False
                    print(f"Less than 11. Error!  [{eachSheet}]")
                    
                else:
                    for eachValue in comparisonIndexRow:
                        if checkRow[eachValue] != comparisonRow[eachValue]:
                            verified = False
                            print(f"{comparisonRow[eachValue]} Out Of Place. Error!  [{eachSheet}]")
                

                if len(checkFirstTradeRow) < 11:
                    verified = False
                    print("checkFirstTradeRow FALSE")
                else:
                    if checkFirstTradeRow[tradeIDPos] == 0 or checkFirstTradeRow[dateTimePos] == 0:
                        print("First Trades NOT Correct.")
                        verified = False
                


                        
                        

                
            

            except:
                print(f"Import Error with sheet {eachSheet}")
                verified = False


            if verified == True:

                sheet = Sheet(self.dfs[eachSheet], index)
                self.sheets.append(sheet)

        # sheet = Sheet(self.dfs["System F"])
        # self.sheets.append(sheet)





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
        print("\n\n\n\n")
    



    def Extrapolate(self):
        for eachSpreadsheet in self.spreadsheets:
            for eachSheet in eachSpreadsheet.sheets:
                eachSheet.monthlyProfits = Monthly_Profit(eachSheet.trades, eachSheet.fakeTrade)


                drawdowns = Calculate_Drawdowns(eachSheet.trades)
                eachSheet.drawdowns = drawdowns


                eachSheet.highestDrawdown = Highest_Drawdown(drawdowns, no_filter=True)

                eachSheet.drawdownsOverFifteenPercent = Filter_Drawdowns(drawdowns)

                eachSheet.periodsOverFifteenPercent = Count_Periods_Drawdown(eachSheet.drawdownsOverFifteenPercent, no_filter=True)

                eachSheet.longestPeriodForFifteenPercent = Longest_Drawdown_Period(drawdowns, moreThan=-1000, lessThan=-15.00)
                eachSheet.longestPeriodForAll = Longest_Drawdown_Period(drawdowns)

                eachSheet.averageDrawdownPeriodForFifteen = Average_Drawdown_Period(drawdowns)

                eachSheet.maxConsecutiveLosses = Max_Consecutive_Losses(eachSheet.trades)


                eachSheet.averageWin = Average_Win(eachSheet.trades)
                eachSheet.highestWin = Highest_Win(eachSheet.trades)
                eachSheet.averageLoss = Average_Loss(eachSheet.trades)
                eachSheet.totalTrades = Total_Trades(eachSheet.trades)
                eachSheet.totalWins = Total_Wins(eachSheet.trades)
                eachSheet.totalLosses = Total_Losses(eachSheet.trades)
                eachSheet.winRate = Win_Rate(eachSheet.trades)

                eachSheet.totalBacktestDays = Total_Backtest_Period(eachSheet.trades, days=True)
                eachSheet.totalBacktestMonths = Total_Backtest_Period(eachSheet.trades, months=True)
                eachSheet.totalBacktestYears = Total_Backtest_Period(eachSheet.trades, years=True)
        

        # for eachSpreadsheet in self.spreadsheets:
        #     for eachSheet in eachSpreadsheet.sheets:
        #         monthlyProfits = Monthly_Profit(eachSheet.trades, eachSheet.fakeTrade)
        #         for eachMonth in monthlyProfits:
        #             print(eachMonth[-1])


        #         drawdowns = Calculate_Drawdowns(eachSheet.trades)

        #         highestDrawdown = Highest_Drawdown(drawdowns, no_filter=True)
        #         print(highestDrawdown.percentageChange)

        #         drawdownsOverFifteenPercent = Filter_Drawdowns(drawdowns)

        #         periodsOverFifteenPercent = Count_Periods_Drawdown(drawdownsOverFifteenPercent, no_filter=True)
        #         print(periodsOverFifteenPercent)

        #         longestPeriodForFifteenPercent = Longest_Drawdown_Period(drawdowns, moreThan=-1000, lessThan=-15.00)
        #         print(longestPeriodForFifteenPercent.daysInDrawdown)
        #         longestPeriodForAll = Longest_Drawdown_Period(drawdowns)
        #         print(longestPeriodForAll.daysInDrawdown)

        #         averageDrawdownPeriodForFifteen = Average_Drawdown_Period(drawdowns)
        #         print(averageDrawdownPeriodForFifteen)

        #         Max_Consecutive_Losses(eachSheet.trades)

        #         print("Here")
        #         print(Average_Win(eachSheet.trades))
        #         print(Highest_Win(eachSheet.trades))
        #         print(Average_Loss(eachSheet.trades))
        #         print(Total_Trades(eachSheet.trades))
        #         print(Total_Wins(eachSheet.trades))
        #         print(Total_Losses(eachSheet.trades))
        #         print(Win_Rate(eachSheet.trades))

        #         print(Total_Backtest_Period(eachSheet.trades, days=True))
        #         print(Total_Backtest_Period(eachSheet.trades, months=True))
        #         print(Total_Backtest_Period(eachSheet.trades, years=True))
        #         print("finished")










def main():
    pass
            
    





if __name__ == "__main__":
    main()