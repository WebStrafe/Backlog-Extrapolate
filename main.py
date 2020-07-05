from backtester import Backtest
from extrapolate import Monthly_Profit
import os
from os import path








def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/Imports"

    backtest = Backtest(path)

    for eachSpreadsheet in backtest.spreadsheets:
        for eachSheet in eachSpreadsheet.sheets:
            Monthly_Profit(eachSheet.trades, eachSheet.fakeTrade)




if __name__ == "__main__":
    main()