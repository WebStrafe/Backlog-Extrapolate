from backtester import Backtest
from extrapolate import Monthly_Profit
from extrapolate import Calculate_Drawdowns
import os
from os import path








def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/Imports"

    backtest = Backtest(path)

    for eachSpreadsheet in backtest.spreadsheets:
        for eachSheet in eachSpreadsheet.sheets:
            monthlyProfits = Monthly_Profit(eachSheet.trades, eachSheet.fakeTrade)
            for eachMonth in monthlyProfits:
                print(eachMonth[-1])


            Calculate_Drawdowns(eachSheet.trades)






if __name__ == "__main__":
    main()